"""
量化特征提取模块
提取样本股票的量化特征，进行数据建模
基于最新的多因子选股策略和机器学习方法
"""
from .data_provider import HistoricalDataProvider
from quant_system.models.stock_data import StockData
import numpy as np
import pandas as pd
import pandas_ta as ta
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Tuple, Any
import logging
from sklearn.preprocessing import StandardScaler, RobustScaler
from sklearn.decomposition import PCA
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
import warnings
warnings.filterwarnings('ignore')


logger = logging.getLogger(__name__)


class QuantitativeFeatureExtractor:
    """量化特征提取器"""

    def __init__(self):
        """初始化特征提取器"""
        self.feature_names = []
        self.scaler = RobustScaler()  # 使用RobustScaler处理异常值
        self.pca = None
        self.feature_importance = {}

        logger.info("量化特征提取器初始化完成")

    def extract_features(self, stock_data: List[StockData], lookback_days: int = 60) -> Dict[str, float]:
        """
        提取单只股票的量化特征

        Args:
            stock_data: 股票历史数据
            lookback_days: 回看天数

        Returns:
            特征字典
        """
        if len(stock_data) < lookback_days:
            logger.warning(f"数据不足，需要{lookback_days}天，实际{len(stock_data)}天")
            return {}

        # 按日期排序
        stock_data.sort(key=lambda x: x.date)

        # 转换为numpy数组便于计算
        closes = np.array([d.close_price for d in stock_data])
        opens = np.array([d.open_price for d in stock_data])
        highs = np.array([d.high_price for d in stock_data])
        lows = np.array([d.low_price for d in stock_data])
        volumes = np.array([d.volume for d in stock_data])
        amounts = np.array([d.amount for d in stock_data])

        features = {}

        # 1. 价格相关特征
        features.update(self._extract_price_features(
            closes, opens, highs, lows))

        # 2. 成交量特征
        features.update(self._extract_volume_features(
            volumes, amounts, closes))

        # 3. 技术指标特征
        features.update(self._extract_technical_features(
            closes, highs, lows, volumes))

        # 4. 动量特征
        features.update(self._extract_momentum_features(closes))

        # 5. 波动率特征
        features.update(self._extract_volatility_features(closes, highs, lows))

        # 6. 趋势特征
        features.update(self._extract_trend_features(closes))

        # 7. 形态特征
        features.update(self._extract_pattern_features(
            opens, highs, lows, closes))

        return features

    def _extract_price_features(self, closes: np.ndarray, opens: np.ndarray,
                                highs: np.ndarray, lows: np.ndarray) -> Dict[str, float]:
        """提取价格相关特征"""
        features = {}

        # 当前价格水平
        features['current_price'] = closes[-1]
        features['price_change_1d'] = (
            closes[-1] - closes[-2]) / closes[-2] if len(closes) > 1 else 0
        features['price_change_5d'] = (
            closes[-1] - closes[-6]) / closes[-6] if len(closes) > 5 else 0
        features['price_change_20d'] = (
            closes[-1] - closes[-21]) / closes[-21] if len(closes) > 20 else 0

        # 价格位置特征
        recent_high = np.max(
            highs[-20:]) if len(highs) >= 20 else np.max(highs)
        recent_low = np.min(lows[-20:]) if len(lows) >= 20 else np.min(lows)

        if recent_high > recent_low:
            features['price_position'] = (
                closes[-1] - recent_low) / (recent_high - recent_low)
        else:
            features['price_position'] = 0.5

        # 价格相对强度
        features['high_low_ratio'] = np.mean(
            highs[-10:] / lows[-10:]) if len(highs) >= 10 else 1
        features['open_close_ratio'] = np.mean(
            closes[-10:] / opens[-10:]) if len(opens) >= 10 else 1

        return features

    def _extract_volume_features(self, volumes: np.ndarray, amounts: np.ndarray,
                                 closes: np.ndarray) -> Dict[str, float]:
        """提取成交量特征"""
        features = {}

        # 成交量指标
        features['volume_ratio_5d'] = np.mean(
            volumes[-5:]) / np.mean(volumes[-20:]) if len(volumes) >= 20 else 1
        features['volume_ratio_10d'] = np.mean(
            volumes[-10:]) / np.mean(volumes[-20:]) if len(volumes) >= 20 else 1

        # 量价关系
        price_changes = np.diff(closes)
        volume_changes = np.diff(volumes)

        if len(price_changes) > 0 and len(volume_changes) > 0:
            # 价涨量增的天数比例
            up_volume_days = np.sum((price_changes > 0) & (volume_changes > 0))
            total_up_days = np.sum(price_changes > 0)
            features['up_volume_ratio'] = up_volume_days / \
                total_up_days if total_up_days > 0 else 0
        else:
            features['up_volume_ratio'] = 0

        # 换手率相关（简化计算）
        if len(amounts) > 0 and len(closes) > 0:
            features['turnover_ratio'] = np.mean(
                amounts[-5:]) / (np.mean(closes[-5:]) * 1e8)  # 简化的换手率
        else:
            features['turnover_ratio'] = 0

        return features

    def _extract_technical_features(self, closes: np.ndarray, highs: np.ndarray,
                                    lows: np.ndarray, volumes: np.ndarray) -> Dict[str, float]:
        """提取技术指标特征"""
        features = {}

        try:
            # 转为DataFrame，pandas-ta要求Series
            df = pd.DataFrame({
                'close': closes,
                'high': highs,
                'low': lows,
                'volume': volumes
            })
            # 移动平均线
            ma5 = ta.sma(df['close'], length=5)
            ma10 = ta.sma(df['close'], length=10)
            ma20 = ta.sma(df['close'], length=20)

            if not np.isnan(ma5.iloc[-1]):
                features['ma5_ratio'] = closes[-1] / ma5.iloc[-1] - 1
            if not np.isnan(ma10.iloc[-1]):
                features['ma10_ratio'] = closes[-1] / ma10.iloc[-1] - 1
            if not np.isnan(ma20.iloc[-1]):
                features['ma20_ratio'] = closes[-1] / ma20.iloc[-1] - 1

            # 均线多头排列
            if not (np.isnan(ma5.iloc[-1]) or np.isnan(ma10.iloc[-1]) or np.isnan(ma20.iloc[-1])):
                features['ma_bullish'] = 1 if ma5.iloc[-1] > ma10.iloc[-1] > ma20.iloc[-1] else 0

            # RSI（多周期）
            for rsi_len in [5, 10, 14, 20]:
                rsi = ta.rsi(df['close'], length=rsi_len)
                if not np.isnan(rsi.iloc[-1]):
                    features[f'rsi_{rsi_len}'] = rsi.iloc[-1]

            # MACD（多周期）
            for fast, slow, signal in [(12,26,9), (5,35,5), (8,21,9)]:
                macd = ta.macd(df['close'], fast=fast, slow=slow, signal=signal)
                if macd is not None and not macd.isnull().values.any():
                    features[f'macd_{fast}_{slow}_{signal}'] = macd[f'MACD_{fast}_{slow}_{signal}'].iloc[-1]
                    features[f'macd_signal_{fast}_{slow}_{signal}'] = macd[f'MACDs_{fast}_{slow}_{signal}'].iloc[-1]
                    features[f'macd_hist_{fast}_{slow}_{signal}'] = macd[f'MACDh_{fast}_{slow}_{signal}'].iloc[-1]

            # 布林带（多周期）
            for bb_len in [10, 20, 30]:
                bbands = ta.bbands(df['close'], length=bb_len)
                if bbands is not None and not bbands.isnull().values.any():
                    upper = bbands[f'BBU_{bb_len}_2.0'].iloc[-1]
                    middle = bbands[f'BBM_{bb_len}_2.0'].iloc[-1]
                    lower = bbands[f'BBL_{bb_len}_2.0'].iloc[-1]
                    if not np.isnan(upper):
                        features[f'bb_position_{bb_len}'] = (closes[-1] - lower) / (upper - lower) if (upper - lower) != 0 else 0.5
                        features[f'bb_width_{bb_len}'] = (upper - lower) / middle if middle != 0 else 0

            # WILLR 威廉指标
            willr = ta.willr(df['high'], df['low'], df['close'], length=14)
            if not np.isnan(willr.iloc[-1]):
                features['willr'] = willr.iloc[-1]

            # CCI 商品通道指数
            cci = ta.cci(df['high'], df['low'], df['close'], length=14)
            if not np.isnan(cci.iloc[-1]):
                features['cci'] = cci.iloc[-1]

            # MFI 资金流量指标
            mfi = ta.mfi(df['high'], df['low'], df['close'], df['volume'], length=14)
            if not np.isnan(mfi.iloc[-1]):
                features['mfi'] = mfi.iloc[-1]

            # BIAS 乖离率（多周期）
            for bias_len in [6, 12, 24]:
                bias = ta.bias(df['close'], length=bias_len)
                if not np.isnan(bias.iloc[-1]):
                    features[f'bias_{bias_len}'] = bias.iloc[-1]

            # ATR 真实波动幅度（多周期）
            for atr_len in [7, 14, 21]:
                atr = ta.atr(df['high'], df['low'], df['close'], length=atr_len)
                if not np.isnan(atr.iloc[-1]):
                    features[f'atr_{atr_len}'] = atr.iloc[-1] / closes[-1] if closes[-1] != 0 else 0

            # KDJ (STOCH)
            stoch = ta.stoch(df['high'], df['low'], df['close'])
            if stoch is not None and not stoch.isnull().values.any():
                k = stoch['STOCHk_14_3_3'].iloc[-1]
                d = stoch['STOCHd_14_3_3'].iloc[-1]
                features['kdj_k'] = k
                features['kdj_d'] = d
                features['kdj_j'] = 3 * k - 2 * d

        except Exception as e:
            logger.debug(f"技术指标计算错误: {e}")

        return features

    def _extract_momentum_features(self, closes: np.ndarray) -> Dict[str, float]:
        """提取动量特征"""
        features = {}

        # 不同周期的动量
        periods = [3, 5, 10, 20]
        for period in periods:
            if len(closes) > period:
                momentum = (closes[-1] - closes[-period-1]) / closes[-period-1]
                features[f'momentum_{period}d'] = momentum

        # 动量加速度
        if len(closes) > 10:
            mom_5 = (closes[-1] - closes[-6]) / closes[-6]
            mom_10 = (closes[-6] - closes[-11]) / closes[-11]
            features['momentum_acceleration'] = mom_5 - mom_10

        # 相对强度
        if len(closes) > 20:
            recent_return = (closes[-1] - closes[-11]) / closes[-11]
            past_return = (closes[-11] - closes[-21]) / closes[-21]
            features['relative_strength'] = recent_return - past_return

        return features

    def _extract_volatility_features(self, closes: np.ndarray, highs: np.ndarray,
                                     lows: np.ndarray) -> Dict[str, float]:
        """提取波动率特征"""
        features = {}

        # 收益率波动率
        if len(closes) > 1:
            returns = np.diff(closes) / closes[:-1]
            features['volatility_5d'] = np.std(
                returns[-5:]) if len(returns) >= 5 else 0
            features['volatility_20d'] = np.std(
                returns[-20:]) if len(returns) >= 20 else 0

        # 真实波动率 (ATR)
        try:
            atr = ta.atr(highs, lows, closes, length=14)
            if not np.isnan(atr.iloc[-1]):
                features['atr'] = atr.iloc[-1] / closes[-1]  # 标准化ATR
        except:
            features['atr'] = 0

        # 高低价差
        if len(highs) > 0 and len(lows) > 0:
            hl_ratio = (highs - lows) / closes
            features['avg_hl_ratio'] = np.mean(
                hl_ratio[-10:]) if len(hl_ratio) >= 10 else 0

        return features

    def _extract_trend_features(self, closes: np.ndarray) -> Dict[str, float]:
        """提取趋势特征"""
        features = {}

        # 线性回归趋势
        if len(closes) >= 20:
            x = np.arange(len(closes[-20:]))
            y = closes[-20:]

            # 计算线性回归斜率
            slope = np.polyfit(x, y, 1)[0]
            features['trend_slope_20d'] = slope / np.mean(y)  # 标准化斜率

            # R平方（趋势强度）
            y_pred = np.polyval([slope, np.polyfit(x, y, 1)[1]], x)
            ss_res = np.sum((y - y_pred) ** 2)
            ss_tot = np.sum((y - np.mean(y)) ** 2)
            features['trend_r2_20d'] = 1 - \
                (ss_res / ss_tot) if ss_tot > 0 else 0

        # 趋势一致性
        if len(closes) >= 10:
            short_trend = closes[-1] > closes[-6]  # 5日趋势
            long_trend = closes[-1] > closes[-11]  # 10日趋势
            features['trend_consistency'] = 1 if short_trend == long_trend else 0

        return features

    def _extract_pattern_features(self, opens: np.ndarray, highs: np.ndarray,
                                  lows: np.ndarray, closes: np.ndarray) -> Dict[str, float]:
        """提取形态特征"""
        features = {}

        # K线形态
        if len(closes) >= 3:
            # 连续上涨天数
            up_days = 0
            for i in range(len(closes)-1, 0, -1):
                if closes[i] > closes[i-1]:
                    up_days += 1
                else:
                    break
            features['consecutive_up_days'] = up_days

            # 连续下跌天数
            down_days = 0
            for i in range(len(closes)-1, 0, -1):
                if closes[i] < closes[i-1]:
                    down_days += 1
                else:
                    break
            features['consecutive_down_days'] = down_days

        # 影线比例
        if len(opens) > 0:
            # 上影线比例
            upper_shadow = (highs - np.maximum(opens, closes)
                            ) / (highs - lows + 1e-8)
            features['avg_upper_shadow'] = np.mean(
                upper_shadow[-5:]) if len(upper_shadow) >= 5 else 0

            # 下影线比例
            lower_shadow = (np.minimum(opens, closes) -
                            lows) / (highs - lows + 1e-8)
            features['avg_lower_shadow'] = np.mean(
                lower_shadow[-5:]) if len(lower_shadow) >= 5 else 0

        # 实体大小
        if len(opens) > 0 and len(closes) > 0:
            body_size = np.abs(closes - opens) / (highs - lows + 1e-8)
            features['avg_body_size'] = np.mean(
                body_size[-5:]) if len(body_size) >= 5 else 0

        return features

    def extract_batch_features(self, sample_stocks: List[Dict],
                               data_provider: HistoricalDataProvider) -> pd.DataFrame:
        """
        批量提取特征

        Args:
            sample_stocks: 样本股票列表
            data_provider: 数据提供者

        Returns:
            特征DataFrame
        """
        logger.info(f"开始批量提取{len(sample_stocks)}只股票的特征")

        feature_list = []

        for i, stock_info in enumerate(sample_stocks):
            if i % 50 == 0:
                logger.info(f"已处理 {i}/{len(sample_stocks)} 只股票")

            try:
                code = stock_info['code']
                start_date = stock_info['start_date']

                # 获取更长的历史数据用于特征计算
                feature_start_date = start_date - timedelta(days=100)
                historical_data = data_provider.get_historical_data(
                    code, feature_start_date, start_date
                )

                if len(historical_data) >= 60:  # 确保有足够数据
                    features = self.extract_features(historical_data)

                    # 添加基本信息
                    features['code'] = code
                    features['name'] = stock_info['name']
                    features['target_return'] = stock_info['total_return']
                    features['target_drawdown'] = stock_info['max_drawdown']

                    feature_list.append(features)

            except Exception as e:
                logger.debug(f"提取{stock_info['code']}特征时出错: {e}")
                continue

        if not feature_list:
            logger.warning("没有成功提取到任何特征")
            return pd.DataFrame()

        # 转换为DataFrame
        df = pd.DataFrame(feature_list)

        # 记录特征名称
        self.feature_names = [col for col in df.columns if col not in [
            'code', 'name', 'target_return', 'target_drawdown']]

        logger.info(f"特征提取完成，共{len(df)}只股票，{len(self.feature_names)}个特征")

        return df

    def build_predictive_model(self, feature_df: pd.DataFrame) -> Dict:
        """
        构建预测模型

        Args:
            feature_df: 特征DataFrame

        Returns:
            模型评估结果
        """
        if feature_df.empty:
            return {}

        logger.info("开始构建预测模型")

        # 准备数据
        X = feature_df[self.feature_names].fillna(0)
        y = feature_df['target_return']

        # 数据标准化
        X_scaled = self.scaler.fit_transform(X)

        # 划分训练测试集
        split_idx = int(len(X_scaled) * 0.8)
        X_train, X_test = X_scaled[:split_idx], X_scaled[split_idx:]
        y_train, y_test = y[:split_idx], y[split_idx:]

        # 训练随机森林模型
        model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            n_jobs=-1
        )

        model.fit(X_train, y_train)

        # 预测和评估
        y_pred_train = model.predict(X_train)
        y_pred_test = model.predict(X_test)

        # 计算评估指标
        train_r2 = r2_score(y_train, y_pred_train)
        test_r2 = r2_score(y_test, y_pred_test)
        train_mse = mean_squared_error(y_train, y_pred_train)
        test_mse = mean_squared_error(y_test, y_pred_test)

        # 特征重要性
        feature_importance = dict(
            zip(self.feature_names, model.feature_importances_))
        self.feature_importance = dict(sorted(feature_importance.items(),
                                              key=lambda x: x[1], reverse=True))

        # PCA分析
        self.pca = PCA(n_components=min(10, len(self.feature_names)))
        X_pca = self.pca.fit_transform(X_scaled)

        results = {
            'model_performance': {
                'train_r2': train_r2,
                'test_r2': test_r2,
                'train_mse': train_mse,
                'test_mse': test_mse
            },
            'feature_importance': self.feature_importance,
            'top_features': list(self.feature_importance.keys())[:10],
            'pca_explained_variance': self.pca.explained_variance_ratio_.tolist(),
            'total_features': len(self.feature_names),
            'sample_size': len(feature_df)
        }

        logger.info(f"模型构建完成，测试R²: {test_r2:.3f}")

        return results


if __name__ == "__main__":
    # 测试特征提取器
    from .data_provider import HistoricalDataProvider

    print("测试量化特征提取模块...")

    # 创建特征提取器和数据提供者
    extractor = QuantitativeFeatureExtractor()
    data_provider = HistoricalDataProvider()

    # 获取测试数据
    stock_list = data_provider.get_stock_list('A')
    if stock_list:
        test_code = stock_list[0][0]
        end_date = date.today()
        start_date = end_date - timedelta(days=100)

        print(f"测试提取{test_code}的特征...")
        historical_data = data_provider.get_historical_data(
            test_code, start_date, end_date)

        if historical_data:
            features = extractor.extract_features(historical_data)
            print(f"提取到{len(features)}个特征:")

            # 显示部分特征
            for i, (name, value) in enumerate(features.items()):
                if i < 10:  # 只显示前10个
                    print(f"  {name}: {value:.4f}")
                elif i == 10:
                    print("  ...")
                    break
        else:
            print("未获取到历史数据")

    print("测试完成！")
