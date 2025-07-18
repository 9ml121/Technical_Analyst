"""
量化特征提取模块 - 微服务版本
提取样本股票的量化特征，进行数据建模
基于最新的多因子选股策略和机器学习方法
"""
import warnings
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.ensemble import RandomForestRegressor
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler, RobustScaler
import logging
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, date, timedelta
import pandas_ta as ta
import pandas as pd
import numpy as np

# 导入微服务架构的共享模型
from shared.models.market_data import StockData

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
            for fast, slow, signal in [(12, 26, 9), (5, 35, 5), (8, 21, 9)]:
                macd = ta.macd(df['close'], fast=fast,
                               slow=slow, signal=signal)
                if macd is not None and not macd.empty:
                    if not np.isnan(macd.iloc[-1, 0]):
                        features[f'macd_{fast}_{slow}'] = macd.iloc[-1, 0]
                    if not np.isnan(macd.iloc[-1, 1]):
                        features[f'macd_signal_{fast}_{slow}'] = macd.iloc[-1, 1]

            # 布林带
            bb = ta.bbands(df['close'], length=20)
            if bb is not None and not bb.empty:
                if not np.isnan(bb.iloc[-1, 0]):
                    features['bb_upper'] = bb.iloc[-1, 0]
                if not np.isnan(bb.iloc[-1, 1]):
                    features['bb_middle'] = bb.iloc[-1, 1]
                if not np.isnan(bb.iloc[-1, 2]):
                    features['bb_lower'] = bb.iloc[-1, 2]
                if not np.isnan(bb.iloc[-1, 3]):
                    features['bb_width'] = bb.iloc[-1, 3]

            # KDJ
            kdj = ta.stoch(df['high'], df['low'], df['close'], k=14, d=3)
            if kdj is not None and not kdj.empty:
                if not np.isnan(kdj.iloc[-1, 0]):
                    features['kdj_k'] = kdj.iloc[-1, 0]
                if not np.isnan(kdj.iloc[-1, 1]):
                    features['kdj_d'] = kdj.iloc[-1, 1]

        except Exception as e:
            logger.debug(f"计算技术指标时出错: {e}")

        return features

    def _extract_momentum_features(self, closes: np.ndarray) -> Dict[str, float]:
        """提取动量特征"""
        features = {}

        # 动量指标
        for period in [5, 10, 20, 30]:
            if len(closes) > period:
                momentum = (closes[-1] - closes[-period-1]) / closes[-period-1]
                features[f'momentum_{period}d'] = momentum

        # 相对强度
        if len(closes) >= 20:
            # 相对于20日均价的强度
            ma20 = np.mean(closes[-20:])
            features['relative_strength'] = closes[-1] / ma20 - 1

        # 价格加速度
        if len(closes) >= 10:
            momentum_5d = (closes[-1] - closes[-6]) / \
                closes[-6] if len(closes) > 5 else 0
            momentum_10d = (closes[-1] - closes[-11]) / \
                closes[-11] if len(closes) > 10 else 0
            features['momentum_acceleration'] = momentum_5d - momentum_10d

        return features

    def _extract_volatility_features(self, closes: np.ndarray, highs: np.ndarray,
                                     lows: np.ndarray) -> Dict[str, float]:
        """提取波动率特征"""
        features = {}

        # 历史波动率
        for period in [5, 10, 20, 30]:
            if len(closes) > period:
                # 修复切片边界问题
                price_slice = closes[-period:]
                returns = np.diff(price_slice) / price_slice[:-1]
                volatility = np.std(returns) * np.sqrt(252)  # 年化波动率
                features[f'volatility_{period}d'] = volatility

        # 真实波动率（基于高低价）
        if len(highs) >= 20 and len(lows) >= 20:
            true_ranges = []
            for i in range(1, min(20, len(highs))):
                tr = max(highs[i] - lows[i],
                         abs(highs[i] - closes[i-1]),
                         abs(lows[i] - closes[i-1]))
                true_ranges.append(tr)

            if true_ranges:
                atr = np.mean(true_ranges)
                features['atr_20d'] = atr
                features['atr_ratio'] = atr / \
                    closes[-1] if closes[-1] > 0 else 0

        return features

    def _extract_trend_features(self, closes: np.ndarray) -> Dict[str, float]:
        """提取趋势特征"""
        features = {}

        # 线性回归趋势
        for period in [10, 20, 30]:
            if len(closes) >= period:
                x = np.arange(period)
                y = closes[-period:]

                # 线性回归
                slope, intercept = np.polyfit(x, y, 1)
                features[f'trend_slope_{period}d'] = slope
                features[f'trend_strength_{period}d'] = abs(
                    slope) / np.mean(y) if np.mean(y) > 0 else 0

        # 趋势一致性
        if len(closes) >= 20:
            # 计算多个周期的趋势方向一致性
            trends = []
            for period in [5, 10, 15, 20]:
                if len(closes) >= period:
                    trend = 1 if closes[-1] > closes[-period] else -1
                    trends.append(trend)

            if trends:
                features['trend_consistency'] = np.mean(trends)

        return features

    def _extract_pattern_features(self, opens: np.ndarray, highs: np.ndarray,
                                  lows: np.ndarray, closes: np.ndarray) -> Dict[str, float]:
        """提取形态特征"""
        features = {}

        # 蜡烛图形态
        if len(closes) >= 3:
            # 锤子线
            body = abs(closes[-1] - opens[-1])
            lower_shadow = min(opens[-1], closes[-1]) - lows[-1]
            upper_shadow = highs[-1] - max(opens[-1], closes[-1])

            features['hammer'] = 1 if (
                lower_shadow > 2 * body and upper_shadow < body) else 0

            # 上吊线
            features['hanging_man'] = 1 if (
                upper_shadow > 2 * body and lower_shadow < body) else 0

        # 缺口
        if len(closes) >= 2:
            gap_up = opens[-1] > highs[-2]
            gap_down = lows[-1] < closes[-2]
            features['gap_up'] = 1 if gap_up else 0
            features['gap_down'] = 1 if gap_down else 0

        # 价格突破
        if len(closes) >= 20:
            recent_high = np.max(closes[-20:-1])
            recent_low = np.min(closes[-20:-1])

            features['breakout_high'] = 1 if closes[-1] > recent_high else 0
            features['breakout_low'] = 1 if closes[-1] < recent_low else 0

        return features

    def extract_batch_features(self, stock_data_dict: Dict[str, List[StockData]]) -> pd.DataFrame:
        """
        批量提取多只股票的特征

        Args:
            stock_data_dict: 股票代码到股票数据的映射

        Returns:
            特征DataFrame
        """
        features_list = []

        for code, stock_data in stock_data_dict.items():
            try:
                features = self.extract_features(stock_data)
                if features:
                    features['code'] = code
                    features_list.append(features)
            except Exception as e:
                logger.debug(f"提取股票{code}特征时出错: {e}")
                continue

        if not features_list:
            return pd.DataFrame()

        feature_df = pd.DataFrame(features_list)
        self.feature_names = [
            col for col in feature_df.columns if col != 'code']

        logger.info(
            f"批量特征提取完成: {len(feature_df)} 只股票, {len(self.feature_names)} 个特征")
        return feature_df

    def build_predictive_model(self, feature_df: pd.DataFrame, target_col: str = 'future_return') -> Dict:
        """
        构建预测模型

        Args:
            feature_df: 特征DataFrame
            target_col: 目标变量列名

        Returns:
            模型性能字典
        """
        if target_col not in feature_df.columns:
            logger.error(f"目标变量 {target_col} 不存在")
            return {}

        # 准备数据
        X = feature_df.drop(['code', target_col], axis=1, errors='ignore')
        y = feature_df[target_col]

        # 数据预处理
        X = X.fillna(0)

        # 特征选择
        from sklearn.feature_selection import SelectKBest, f_regression
        selector = SelectKBest(f_regression, k=min(20, len(X.columns)))
        X_selected = selector.fit_transform(X, y)
        selected_features = X.columns[selector.get_support()].tolist()

        # 训练模型
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X_selected, y)

        # 模型评估
        y_pred = model.predict(X_selected)
        r2 = r2_score(y, y_pred)
        mse = mean_squared_error(y, y_pred)

        # 特征重要性
        feature_importance = dict(
            zip(selected_features, model.feature_importances_))
        feature_importance = dict(sorted(feature_importance.items(),
                                         key=lambda x: x[1], reverse=True))

        return {
            'r2_score': r2,
            'mse': mse,
            'feature_importance': feature_importance,
            'selected_features': selected_features,
            'model': model
        }

    def get_feature_summary(self) -> Dict[str, Any]:
        """获取特征提取器摘要信息"""
        return {
            'feature_names': self.feature_names,
            'feature_count': len(self.feature_names),
            'scaler_type': type(self.scaler).__name__,
            'pca_components': self.pca.n_components_ if self.pca else None
        }
