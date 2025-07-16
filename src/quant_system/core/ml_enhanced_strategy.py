"""
机器学习增强的量化交易策略
整合传统技术分析和机器学习预测，提高选股和交易决策的准确性
"""
from .feature_extraction import QuantitativeFeatureExtractor
from quant_system.models.strategy_models import TradingSignal, SignalType
from quant_system.models.stock_data import StockData
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.model_selection import TimeSeriesSplit, cross_val_score
from sklearn.feature_selection import SelectKBest, f_regression, RFE
from sklearn.preprocessing import StandardScaler, RobustScaler
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
import numpy as np
import pandas as pd
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Tuple, Any
import logging
from dataclasses import dataclass
import joblib
import warnings
warnings.filterwarnings('ignore')

# 机器学习相关导入

# 项目内部导入

logger = logging.getLogger(__name__)


@dataclass
class ModelConfig:
    """机器学习模型配置"""
    model_type: str  # 'random_forest', 'gradient_boosting', 'linear'
    n_estimators: int = 200
    max_depth: int = 15
    learning_rate: float = 0.1
    feature_selection: str = 'kbest'  # 'kbest', 'rfe', 'none'
    n_features: int = 20
    target_horizon: int = 5  # 预测未来5天的收益率
    retrain_frequency: int = 30  # 每30天重新训练一次


@dataclass
class MLStrategyConfig:
    """机器学习策略配置"""
    name: str
    model_config: ModelConfig
    signal_threshold: float = 0.02  # 信号阈值，预测收益率超过2%才买入
    confidence_threshold: float = 0.6  # 置信度阈值
    position_sizing: str = 'kelly'  # 'kelly', 'equal', 'volatility_adjusted'
    risk_management: Dict[str, float] = None
    description: str = ""


class MLEnhancedStrategy:
    """机器学习增强的量化交易策略"""

    def __init__(self, config: MLStrategyConfig = None):
        """初始化策略"""
        self.config = config or self._get_default_config()
        self.feature_extractor = QuantitativeFeatureExtractor()
        self.model = None
        self.scaler = RobustScaler()
        self.feature_selector = None
        self.feature_names = []
        self.model_performance = {}
        self.last_training_date = None

        # 初始化模型
        self._initialize_model()

        logger.info(f"机器学习增强策略初始化完成: {self.config.name}")

    def _get_default_config(self) -> MLStrategyConfig:
        """获取默认配置"""
        model_config = ModelConfig(
            model_type='random_forest',
            n_estimators=200,
            max_depth=15,
            feature_selection='kbest',
            n_features=20,
            target_horizon=5
        )

        risk_management = {
            "max_position_pct": 0.15,
            "max_positions": 8,
            "stop_loss_pct": 0.04,
            "take_profit_pct": 0.08,
            "max_drawdown_pct": 0.08,
            "min_confidence": 0.6
        }

        return MLStrategyConfig(
            name="机器学习增强策略",
            model_config=model_config,
            signal_threshold=0.02,
            confidence_threshold=0.6,
            position_sizing='kelly',
            risk_management=risk_management,
            description="基于机器学习的多因子选股策略，结合技术指标和预测模型"
        )

    def _initialize_model(self):
        """初始化机器学习模型"""
        model_config = self.config.model_config

        # 选择模型类型
        if model_config.model_type == 'random_forest':
            self.model = RandomForestRegressor(
                n_estimators=model_config.n_estimators,
                max_depth=model_config.max_depth,
                random_state=42,
                n_jobs=-1
            )
        elif model_config.model_type == 'gradient_boosting':
            self.model = GradientBoostingRegressor(
                n_estimators=model_config.n_estimators,
                max_depth=model_config.max_depth,
                learning_rate=model_config.learning_rate,
                random_state=42
            )
        elif model_config.model_type == 'linear':
            self.model = LinearRegression()
        else:
            raise ValueError(f"不支持的模型类型: {model_config.model_type}")

        # 初始化特征选择器
        if model_config.feature_selection == 'kbest':
            self.feature_selector = SelectKBest(
                f_regression, k=model_config.n_features)
        elif model_config.feature_selection == 'rfe':
            self.feature_selector = RFE(
                estimator=RandomForestRegressor(
                    n_estimators=50, random_state=42),
                n_features_to_select=model_config.n_features
            )

        logger.info(f"模型初始化完成: {model_config.model_type}")

    def prepare_training_data(self, stock_data_list: List[List[StockData]],
                              data_provider=None) -> Tuple[pd.DataFrame, pd.Series]:
        """
        准备训练数据

        Args:
            stock_data_list: 多只股票的历史数据列表
            data_provider: 数据提供者（用于获取未来价格计算目标变量）

        Returns:
            特征DataFrame和目标变量Series
        """
        logger.info("开始准备训练数据...")

        features_list = []
        targets_list = []

        for stock_data in stock_data_list:
            if len(stock_data) < 80:  # 需要足够的历史数据
                continue

            try:
                # 提取特征
                features = self.feature_extractor.extract_features(stock_data)
                if not features:
                    continue

                # 计算目标变量（未来收益率）
                target = self._calculate_future_return(
                    stock_data, self.config.model_config.target_horizon)
                if target is None:
                    continue

                features_list.append(features)
                targets_list.append(target)

            except Exception as e:
                logger.debug(f"处理股票数据时出错: {e}")
                continue

        if not features_list:
            logger.warning("没有成功提取到训练数据")
            return pd.DataFrame(), pd.Series()

        # 转换为DataFrame
        feature_df = pd.DataFrame(features_list)
        target_series = pd.Series(targets_list)

        # 记录特征名称
        self.feature_names = list(feature_df.columns)

        logger.info(
            f"训练数据准备完成: {len(feature_df)} 样本, {len(self.feature_names)} 特征")

        return feature_df, target_series

    def _calculate_future_return(self, stock_data: List[StockData], horizon: int) -> Optional[float]:
        """
        计算未来收益率

        Args:
            stock_data: 股票历史数据
            horizon: 预测周期（天数）

        Returns:
            未来收益率
        """
        if len(stock_data) < horizon + 1:
            return None

        # 按日期排序
        stock_data.sort(key=lambda x: x.date)

        # 当前价格
        current_price = stock_data[-1].close_price

        # 未来价格（如果有足够数据）
        if len(stock_data) >= horizon:
            future_price = stock_data[-horizon-1].close_price
            return (future_price - current_price) / current_price

        return None

    def train_model(self, training_data: Tuple[pd.DataFrame, pd.Series],
                    validation_data: Tuple[pd.DataFrame, pd.Series] = None) -> Dict:
        """
        训练机器学习模型

        Args:
            training_data: 训练数据 (特征, 目标)
            validation_data: 验证数据 (特征, 目标)

        Returns:
            训练结果字典
        """
        X_train, y_train = training_data

        if X_train.empty or y_train.empty:
            logger.error("训练数据为空")
            return {}

        logger.info("开始训练机器学习模型...")

        # 数据预处理
        X_train_clean = X_train.fillna(0)

        # 特征选择
        if self.feature_selector:
            X_train_selected = self.feature_selector.fit_transform(
                X_train_clean, y_train)
            selected_features = X_train_clean.columns[self.feature_selector.get_support(
            )].tolist()
            logger.info(f"特征选择完成，选择了 {len(selected_features)} 个特征")
        else:
            X_train_selected = X_train_clean
            selected_features = list(X_train_clean.columns)

        # 数据标准化
        X_train_scaled = self.scaler.fit_transform(X_train_selected)

        # 训练模型
        self.model.fit(X_train_scaled, y_train)

        # 模型评估
        y_pred_train = self.model.predict(X_train_scaled)

        # 计算评估指标
        train_r2 = r2_score(y_train, y_pred_train)
        train_mse = mean_squared_error(y_train, y_pred_train)
        train_mae = mean_absolute_error(y_train, y_pred_train)

        # 特征重要性
        if hasattr(self.model, 'feature_importances_'):
            feature_importance = dict(
                zip(selected_features, self.model.feature_importances_))
            feature_importance = dict(sorted(feature_importance.items(),
                                             key=lambda x: x[1], reverse=True))
        else:
            feature_importance = {}

        # 交叉验证
        cv_scores = cross_val_score(self.model, X_train_scaled, y_train,
                                    cv=TimeSeriesSplit(n_splits=5), scoring='r2')

        # 验证集评估
        validation_results = {}
        if validation_data:
            X_val, y_val = validation_data
            X_val_clean = X_val.fillna(0)

            if self.feature_selector:
                X_val_selected = self.feature_selector.transform(X_val_clean)
            else:
                X_val_selected = X_val_clean

            X_val_scaled = self.scaler.transform(X_val_selected)
            y_pred_val = self.model.predict(X_val_scaled)

            validation_results = {
                'val_r2': r2_score(y_val, y_pred_val),
                'val_mse': mean_squared_error(y_val, y_pred_val),
                'val_mae': mean_absolute_error(y_val, y_pred_val)
            }

        # 更新模型性能记录
        self.model_performance = {
            'train_r2': train_r2,
            'train_mse': train_mse,
            'train_mae': train_mae,
            'cv_mean': cv_scores.mean(),
            'cv_std': cv_scores.std(),
            'feature_importance': feature_importance,
            'top_features': list(feature_importance.keys())[:10],
            'training_date': datetime.now(),
            **validation_results
        }

        self.last_training_date = datetime.now()

        logger.info(
            f"模型训练完成，训练R²: {train_r2:.3f}, CV R²: {cv_scores.mean():.3f}")

        return self.model_performance

    def predict_return(self, stock_data: List[StockData]) -> Tuple[float, float]:
        """
        预测股票未来收益率

        Args:
            stock_data: 股票历史数据

        Returns:
            (预测收益率, 置信度)
        """
        # 修复：判断模型是否已训练
        from sklearn.utils.validation import check_is_fitted
        try:
            check_is_fitted(self.model)
        except Exception:
            logger.warning("模型未训练")
            return 0.0, 0.0

        try:
            # 提取特征
            features = self.feature_extractor.extract_features(stock_data)
            if not features:
                return 0.0, 0.0

            # 转换为DataFrame
            feature_df = pd.DataFrame([features])
            feature_df = feature_df.fillna(0)

            # 特征选择
            if self.feature_selector:
                feature_df_selected = self.feature_selector.transform(
                    feature_df)
            else:
                feature_df_selected = feature_df

            # 数据标准化
            feature_df_scaled = self.scaler.transform(feature_df_selected)

            # 预测
            predicted_return = self.model.predict(feature_df_scaled)[0]

            # 计算置信度（基于模型的不确定性）
            if hasattr(self.model, 'estimators_'):
                # 对于集成模型，使用预测的标准差作为不确定性度量
                predictions = []
                for estimator in self.model.estimators_:
                    pred = estimator.predict(feature_df_scaled)[0]
                    predictions.append(pred)

                confidence = 1.0 - \
                    min(np.std(predictions) * 10, 1.0)  # 标准化到0-1
            else:
                # 对于其他模型，使用固定的置信度
                confidence = 0.7

            return predicted_return, confidence

        except Exception as e:
            logger.debug(f"预测时出错: {e}")
            return 0.0, 0.0

    def generate_trading_signals(self, stock_data: List[StockData],
                                 current_positions: Dict = None) -> List[TradingSignal]:
        """
        生成交易信号

        Args:
            stock_data: 股票数据
            current_positions: 当前持仓

        Returns:
            交易信号列表
        """
        if not stock_data:
            return []

        signals = []
        code = stock_data[0].code
        current_price = stock_data[-1].close_price

        # 预测未来收益率
        predicted_return, confidence = self.predict_return(stock_data)

        # 检查是否需要重新训练模型
        if self._should_retrain():
            logger.info("模型需要重新训练")
            # 这里可以触发重新训练逻辑

        # 生成买入信号
        if current_positions is None or code not in current_positions:
            if (predicted_return > self.config.signal_threshold and
                    confidence > self.config.confidence_threshold):

                signal = TradingSignal(
                    stock_code=code,
                    signal_type=SignalType.BUY,
                    signal_time=stock_data[-1].date,
                    price=current_price,
                    confidence=confidence,
                    reason=f"ML预测收益率: {predicted_return:.2%}, 置信度: {confidence:.2f}",
                    strategy_name=self.config.name
                )
                signals.append(signal)

        # 生成卖出信号
        elif current_positions and code in current_positions:
            position = current_positions[code]
            cost_price = position.get('avg_cost', current_price)
            profit_pct = (current_price - cost_price) / \
                cost_price if cost_price > 0 else 0

            # 卖出条件：预测下跌或达到止盈止损
            should_sell = (
                predicted_return < -self.config.signal_threshold or
                profit_pct >= self.config.risk_management['take_profit_pct'] or
                profit_pct <= -self.config.risk_management['stop_loss_pct']
            )

            if should_sell:
                signal = TradingSignal(
                    stock_code=code,
                    signal_type=SignalType.SELL,
                    signal_time=stock_data[-1].date,
                    price=current_price,
                    confidence=confidence,
                    reason=f"ML预测: {predicted_return:.2%}, 当前盈亏: {profit_pct:.2%}",
                    strategy_name=self.config.name
                )
                signals.append(signal)

        return signals

    def _should_retrain(self) -> bool:
        """判断是否需要重新训练模型"""
        if not self.last_training_date:
            return True

        days_since_training = (datetime.now() - self.last_training_date).days
        return days_since_training >= self.config.model_config.retrain_frequency

    def calculate_position_size(self, signal: TradingSignal, available_capital: float,
                                current_positions: Dict) -> int:
        """
        计算仓位大小

        Args:
            signal: 交易信号
            available_capital: 可用资金
            current_positions: 当前持仓

        Returns:
            股票数量
        """
        if not signal or available_capital <= 0:
            return 0

        risk_config = self.config.risk_management
        max_position_pct = risk_config.get('max_position_pct', 0.15)
        max_positions = risk_config.get('max_positions', 8)

        # 检查持仓数量限制
        if len(current_positions) >= max_positions:
            return 0

        # 根据仓位调整方式计算
        sizing_method = self.config.position_sizing

        if sizing_method == 'kelly':
            # Kelly公式：f = (bp - q) / b
            # 这里简化处理，基于预测收益率和置信度
            win_prob = signal.confidence
            avg_win = abs(signal.confidence * 0.05)  # 假设平均盈利5%
            avg_loss = 0.03  # 假设平均亏损3%

            kelly_ratio = (win_prob * avg_win - (1 - win_prob)
                           * avg_loss) / avg_win
            kelly_ratio = max(0, min(kelly_ratio, 0.25))  # 限制在0-25%

            position_value = available_capital * kelly_ratio

        elif sizing_method == 'equal':
            position_value = available_capital * max_position_pct

        elif sizing_method == 'volatility_adjusted':
            # 根据预测置信度调整仓位
            confidence_adjustment = signal.confidence
            position_value = available_capital * max_position_pct * confidence_adjustment

        else:
            position_value = available_capital * max_position_pct

        # 计算股票数量（向下取整到100股的倍数）
        shares = int(position_value / signal.price / 100) * 100

        return max(shares, 0)

    def save_model(self, file_path: str):
        """保存模型"""
        if self.model:
            model_data = {
                'model': self.model,
                'scaler': self.scaler,
                'feature_selector': self.feature_selector,
                'feature_names': self.feature_names,
                'config': self.config,
                'performance': self.model_performance,
                'last_training_date': self.last_training_date
            }
            joblib.dump(model_data, file_path)
            logger.info(f"模型已保存到: {file_path}")

    def load_model(self, file_path: str) -> bool:
        """加载模型"""
        try:
            model_data = joblib.load(file_path)
            self.model = model_data['model']
            self.scaler = model_data['scaler']
            self.feature_selector = model_data['feature_selector']
            self.feature_names = model_data['feature_names']
            self.config = model_data['config']
            self.model_performance = model_data['performance']
            self.last_training_date = model_data['last_training_date']

            logger.info(f"模型已从 {file_path} 加载")
            return True
        except Exception as e:
            logger.error(f"加载模型失败: {e}")
            return False

    def get_strategy_summary(self) -> Dict:
        """获取策略摘要"""
        return {
            'name': self.config.name,
            'model_type': self.config.model_config.model_type,
            'signal_threshold': self.config.signal_threshold,
            'confidence_threshold': self.config.confidence_threshold,
            'position_sizing': self.config.position_sizing,
            'risk_management': self.config.risk_management,
            'model_performance': self.model_performance,
            'last_training_date': self.last_training_date,
            'description': self.config.description
        }
