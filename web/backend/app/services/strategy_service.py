"""
策略服务
"""

from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
import logging
from datetime import datetime

from app.models.strategy import Strategy
from app.schemas.strategy import (
    StrategyCreate, StrategyUpdate, StrategyConfig,
    StrategyPerformance, StrategyTestResult
)

logger = logging.getLogger(__name__)

class StrategyService:
    """策略服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def create_strategy(self, strategy_data: StrategyCreate) -> Strategy:
        """创建新策略"""
        try:
            # 创建策略实例
            strategy = Strategy(
                name=strategy_data.name,
                description=strategy_data.description,
                type=strategy_data.type,
                version=strategy_data.version,
                config=strategy_data.config,
                risk_config=strategy_data.risk_config or {}
            )
            
            self.db.add(strategy)
            self.db.commit()
            self.db.refresh(strategy)
            
            logger.info(f"创建策略成功: {strategy.name} (ID: {strategy.id})")
            return strategy
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"创建策略失败: {e}")
            raise
    
    async def update_strategy(self, strategy_id: int, strategy_data: StrategyUpdate) -> Strategy:
        """更新策略信息"""
        try:
            strategy = self.db.query(Strategy).filter(
                Strategy.id == strategy_id
            ).first()
            
            if not strategy:
                raise ValueError("策略不存在")
            
            # 检查策略是否正在运行
            if strategy.status == "running" and strategy_data.config:
                raise ValueError("无法修改正在运行的策略配置，请先停止策略")
            
            # 更新字段
            if strategy_data.name is not None:
                strategy.name = strategy_data.name
            if strategy_data.description is not None:
                strategy.description = strategy_data.description
            if strategy_data.version is not None:
                strategy.version = strategy_data.version
            if strategy_data.config is not None:
                strategy.config = strategy_data.config
            if strategy_data.risk_config is not None:
                strategy.risk_config = strategy_data.risk_config
            if strategy_data.status is not None:
                strategy.status = strategy_data.status
            
            strategy.updated_at = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(strategy)
            
            logger.info(f"更新策略成功: {strategy.name} (ID: {strategy.id})")
            return strategy
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"更新策略失败: {e}")
            raise
    
    async def start_strategy(self, strategy_id: int):
        """启动策略"""
        try:
            strategy = self.db.query(Strategy).filter(
                Strategy.id == strategy_id
            ).first()
            
            if not strategy:
                raise ValueError("策略不存在")
            
            if strategy.status == "running":
                raise ValueError("策略已在运行中")
            
            # 验证策略配置
            if not self._validate_strategy_config(strategy.config):
                raise ValueError("策略配置无效")
            
            # 更新策略状态
            strategy.status = "running"
            strategy.last_run_time = datetime.utcnow()
            strategy.updated_at = datetime.utcnow()
            
            self.db.commit()
            
            # TODO: 启动策略执行引擎
            # await self._start_strategy_engine(strategy)
            
            logger.info(f"启动策略成功: {strategy.name} (ID: {strategy.id})")
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"启动策略失败: {e}")
            raise
    
    async def stop_strategy(self, strategy_id: int):
        """停止策略"""
        try:
            strategy = self.db.query(Strategy).filter(
                Strategy.id == strategy_id
            ).first()
            
            if not strategy:
                raise ValueError("策略不存在")
            
            if strategy.status == "stopped":
                raise ValueError("策略已停止")
            
            # 更新策略状态
            strategy.status = "stopped"
            strategy.updated_at = datetime.utcnow()
            
            self.db.commit()
            
            # TODO: 停止策略执行引擎
            # await self._stop_strategy_engine(strategy)
            
            logger.info(f"停止策略成功: {strategy.name} (ID: {strategy.id})")
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"停止策略失败: {e}")
            raise
    
    async def pause_strategy(self, strategy_id: int):
        """暂停策略"""
        try:
            strategy = self.db.query(Strategy).filter(
                Strategy.id == strategy_id
            ).first()
            
            if not strategy:
                raise ValueError("策略不存在")
            
            if strategy.status != "running":
                raise ValueError("只能暂停正在运行的策略")
            
            # 更新策略状态
            strategy.status = "paused"
            strategy.updated_at = datetime.utcnow()
            
            self.db.commit()
            
            logger.info(f"暂停策略成功: {strategy.name} (ID: {strategy.id})")
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"暂停策略失败: {e}")
            raise
    
    async def update_strategy_config(self, strategy_id: int, config: StrategyConfig):
        """更新策略配置"""
        try:
            strategy = self.db.query(Strategy).filter(
                Strategy.id == strategy_id
            ).first()
            
            if not strategy:
                raise ValueError("策略不存在")
            
            if strategy.status == "running":
                raise ValueError("无法修改正在运行的策略配置")
            
            # 更新配置
            new_config = strategy.config.copy() if strategy.config else {}
            config_dict = config.dict(exclude_unset=True)
            
            # 更新基础参数
            for key, value in config_dict.items():
                if value is not None:
                    new_config[key] = value
            
            strategy.config = new_config
            strategy.updated_at = datetime.utcnow()
            
            self.db.commit()
            
            logger.info(f"更新策略配置成功: {strategy.name} (ID: {strategy.id})")
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"更新策略配置失败: {e}")
            raise
    
    async def get_strategy_performance(self, strategy_id: int) -> StrategyPerformance:
        """获取策略性能指标"""
        try:
            strategy = self.db.query(Strategy).filter(
                Strategy.id == strategy_id
            ).first()
            
            if not strategy:
                raise ValueError("策略不存在")
            
            # 计算性能指标（这里使用模拟数据，实际应该从历史数据计算）
            return StrategyPerformance(
                strategy_id=strategy.id,
                strategy_name=strategy.name,
                total_return=strategy.total_return,
                cumulative_return=strategy.total_return,
                annualized_return=strategy.total_return * 2,  # 简化计算
                max_drawdown=strategy.max_drawdown,
                volatility=strategy.volatility,
                sharpe_ratio=strategy.sharpe_ratio,
                sortino_ratio=strategy.sharpe_ratio * 1.2,  # 简化计算
                calmar_ratio=strategy.total_return / abs(strategy.max_drawdown) if strategy.max_drawdown != 0 else 0,
                total_trades=strategy.total_trades,
                win_trades=strategy.win_trades,
                win_rate=strategy.win_rate,
                avg_win=5.2,  # 模拟数据
                avg_loss=-2.8,  # 模拟数据
                profit_factor=1.86,  # 模拟数据
                avg_holding_period=5.5,  # 模拟数据
                max_positions=strategy.get_config_value("max_positions", 10),
                turnover_rate=0.8,  # 模拟数据
                benchmark_return=2.15,  # 模拟数据
                alpha=strategy.total_return - 2.15,  # 简化计算
                beta=1.2,  # 模拟数据
                information_ratio=0.85,  # 模拟数据
                status=strategy.status,
                running_days=strategy.running_days,
                last_update=strategy.updated_at or strategy.created_at
            )
            
        except Exception as e:
            logger.error(f"获取策略性能失败: {e}")
            raise
    
    async def test_strategy(self, strategy_id: int) -> StrategyTestResult:
        """测试策略参数"""
        try:
            strategy = self.db.query(Strategy).filter(
                Strategy.id == strategy_id
            ).first()
            
            if not strategy:
                raise ValueError("策略不存在")
            
            # 验证参数
            validity = self._validate_strategy_config(strategy.config)
            parameter_validity = self._check_parameter_validity(strategy.config)
            
            # 生成建议
            suggestions = self._generate_suggestions(strategy.config)
            
            return StrategyTestResult(
                strategy_id=strategy.id,
                test_status="success" if validity else "failed",
                test_message="参数测试完成" if validity else "参数配置存在问题",
                expected_return=8.5,  # 模拟数据
                expected_risk=12.3,  # 模拟数据
                parameter_validity=parameter_validity,
                suggestions=suggestions,
                test_time=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"测试策略失败: {e}")
            raise
    
    def _validate_strategy_config(self, config: Dict[str, Any]) -> bool:
        """验证策略配置"""
        required_params = ["momentum_period", "buy_threshold", "sell_threshold"]
        
        for param in required_params:
            if param not in config:
                return False
        
        # 验证参数范围
        if config.get("momentum_period", 0) < 5 or config.get("momentum_period", 0) > 60:
            return False
        
        if config.get("buy_threshold", 0) <= 0:
            return False
        
        if config.get("sell_threshold", 0) >= 0:
            return False
        
        return True
    
    def _check_parameter_validity(self, config: Dict[str, Any]) -> Dict[str, bool]:
        """检查参数有效性"""
        return {
            "momentum_period": 5 <= config.get("momentum_period", 0) <= 60,
            "buy_threshold": config.get("buy_threshold", 0) > 0,
            "sell_threshold": config.get("sell_threshold", 0) < 0,
            "max_positions": 1 <= config.get("max_positions", 0) <= 50,
            "max_position_size": 0.01 <= config.get("max_position_size", 0) <= 0.5
        }
    
    def _generate_suggestions(self, config: Dict[str, Any]) -> list[str]:
        """生成优化建议"""
        suggestions = []
        
        momentum_period = config.get("momentum_period", 20)
        if momentum_period < 10:
            suggestions.append("建议将动量周期调整到10天以上，以减少噪音信号")
        elif momentum_period > 30:
            suggestions.append("建议将动量周期调整到30天以下，以提高信号敏感度")
        
        buy_threshold = config.get("buy_threshold", 5.0)
        if buy_threshold < 3.0:
            suggestions.append("买入阈值过低，可能产生过多交易信号")
        elif buy_threshold > 8.0:
            suggestions.append("买入阈值过高，可能错失交易机会")
        
        return suggestions
