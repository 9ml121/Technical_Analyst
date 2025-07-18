"""
机器学习策略相关模型 - 微服务架构共享模型
定义ML策略相关的数据结构和配置
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum
from datetime import date

from .base import TradingSignal, SignalType


class ModelType(Enum):
    """机器学习模型类型"""
    RANDOM_FOREST = "random_forest"
    GRADIENT_BOOSTING = "gradient_boosting"
    LINEAR = "linear"
    XGBOOST = "xgboost"
    LIGHTGBM = "lightgbm"
    NEURAL_NETWORK = "neural_network"


class FeatureSelectionMethod(Enum):
    """特征选择方法"""
    KBEST = "kbest"
    RFE = "rfe"
    NONE = "none"
    LASSO = "lasso"
    RIDGE = "ridge"


class PositionSizingMethod(Enum):
    """仓位分配方法"""
    EQUAL = "equal"
    KELLY = "kelly"
    VOLATILITY_ADJUSTED = "volatility_adjusted"
    RISK_PARITY = "risk_parity"
    MARKOWITZ = "markowitz"


@dataclass
class ModelConfig:
    """机器学习模型配置"""
    model_type: ModelType = ModelType.RANDOM_FOREST
    n_estimators: int = 200
    max_depth: int = 15
    learning_rate: float = 0.1
    feature_selection: FeatureSelectionMethod = FeatureSelectionMethod.KBEST
    n_features: int = 20
    target_horizon: int = 5  # 预测未来5天的收益率
    retrain_frequency: int = 30  # 每30天重新训练一次

    # 高级参数
    min_samples_split: int = 2
    min_samples_leaf: int = 1
    max_features: Optional[str] = None
    random_state: int = 42
    n_jobs: int = -1

    # 正则化参数
    alpha: float = 1.0  # L1正则化
    l1_ratio: float = 0.5  # L1/L2混合比例

    # 早停参数
    early_stopping_rounds: Optional[int] = None
    validation_fraction: float = 0.1


@dataclass
class RiskManagementConfig:
    """风险管理配置"""
    max_position_pct: float = 0.15  # 单只股票最大仓位比例
    max_positions: int = 8  # 最大持仓数量
    stop_loss_pct: float = 0.04  # 止损比例
    take_profit_pct: float = 0.08  # 止盈比例
    max_drawdown_pct: float = 0.08  # 最大回撤限制
    min_confidence: float = 0.6  # 最小置信度
    max_correlation: float = 0.7  # 最大相关性限制
    sector_limit: float = 0.3  # 单一行业最大仓位


@dataclass
class MLStrategyConfig:
    """机器学习策略配置"""
    name: str
    model_config: ModelConfig
    signal_threshold: float = 0.02  # 信号阈值，预测收益率超过2%才买入
    confidence_threshold: float = 0.6  # 置信度阈值
    position_sizing: PositionSizingMethod = PositionSizingMethod.KELLY
    risk_management: RiskManagementConfig = None
    description: str = ""

    # 策略参数
    rebalance_frequency: str = "daily"  # 调仓频率
    min_holding_days: int = 5  # 最小持仓天数
    max_holding_days: int = 60  # 最大持仓天数

    # 特征工程参数
    feature_lookback_days: int = 60  # 特征回看天数
    use_technical_indicators: bool = True
    use_fundamental_indicators: bool = False
    use_sentiment_indicators: bool = False

    # 模型评估参数
    cross_validation_folds: int = 5
    test_size: float = 0.2
    performance_metrics: List[str] = field(
        default_factory=lambda: ["r2", "mae", "rmse"])

    def __post_init__(self):
        """初始化后处理"""
        if self.risk_management is None:
            self.risk_management = RiskManagementConfig()


@dataclass
class ModelPerformance:
    """模型性能指标"""
    model_name: str
    training_date: str
    r2_score: float
    mae: float
    rmse: float
    feature_importance: Dict[str, float] = field(default_factory=dict)
    cross_validation_scores: List[float] = field(default_factory=list)
    test_predictions: List[float] = field(default_factory=list)
    test_actuals: List[float] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MLPrediction:
    """机器学习预测结果"""
    stock_code: str
    predicted_return: float
    confidence: float
    prediction_date: str
    model_version: str
    features_used: List[str] = field(default_factory=list)
    feature_values: Dict[str, float] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MLSignal:
    """机器学习交易信号"""
    stock_code: str
    signal_type: SignalType
    signal_time: date
    price: float
    confidence: float = 0.0
    reason: str = ""
    strategy_name: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    predicted_return: float = 0.0
    model_version: str = ""
    feature_importance: Dict[str, float] = field(default_factory=dict)
    prediction_metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TrainingDataConfig:
    """训练数据配置"""
    start_date: str
    end_date: str
    stock_codes: List[str] = field(default_factory=list)
    min_data_points: int = 80
    target_variable: str = "future_return"
    feature_engineering: Dict[str, Any] = field(default_factory=dict)
    data_cleaning: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ModelMetadata:
    """模型元数据"""
    model_id: str
    version: str
    created_date: str
    last_updated: str
    training_data_info: Dict[str, Any] = field(default_factory=dict)
    hyperparameters: Dict[str, Any] = field(default_factory=dict)
    performance_history: List[ModelPerformance] = field(default_factory=list)
    deployment_info: Dict[str, Any] = field(default_factory=dict)
