"""
策略管理服务
"""
from app.models.strategy import (
    Strategy, StrategyCreate, StrategyUpdate, StrategyExecution,
    StrategyResult, StrategyTemplate, StrategyResponse
)
import sys
import os
import uuid
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import logging
import json

# 添加项目根目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../../'))


logger = logging.getLogger(__name__)


class StrategyService:
    """策略管理服务"""

    def __init__(self):
        self.strategies = {}
        self.executions = {}
        self.templates = {}
        self._init_default_strategies()
        self._init_templates()

    def _init_default_strategies(self):
        """初始化默认策略"""
        try:
            default_strategies = [
                {
                    "id": "momentum_001",
                    "name": "动量策略",
                    "description": "基于价格动量的选股策略",
                    "category": "momentum",
                    "author": "system",
                    "version": "1.0.0",
                    "parameters": {
                        "lookback_period": 20,
                        "threshold": 0.05,
                        "max_positions": 10
                    },
                    "status": "active",
                    "created_at": datetime.now(),
                    "updated_at": datetime.now()
                },
                {
                    "id": "mean_reversion_001",
                    "name": "均值回归策略",
                    "description": "基于价格均值回归的交易策略",
                    "category": "mean_reversion",
                    "author": "system",
                    "version": "1.0.0",
                    "parameters": {
                        "window": 30,
                        "std_dev": 2.0,
                        "max_positions": 10
                    },
                    "status": "active",
                    "created_at": datetime.now(),
                    "updated_at": datetime.now()
                },
                {
                    "id": "ml_enhanced_001",
                    "name": "机器学习增强策略",
                    "description": "使用机器学习模型增强的选股策略",
                    "category": "ml",
                    "author": "system",
                    "version": "1.0.0",
                    "parameters": {
                        "model": "random_forest",
                        "features": 10,
                        "lookback_period": 60,
                        "max_positions": 10
                    },
                    "status": "active",
                    "created_at": datetime.now(),
                    "updated_at": datetime.now()
                }
            ]

            for strategy_data in default_strategies:
                strategy = Strategy(**strategy_data)
                self.strategies[strategy.id] = strategy

            logger.info(f"初始化了 {len(default_strategies)} 个默认策略")

        except Exception as e:
            logger.error(f"初始化默认策略失败: {e}")

    def _init_templates(self):
        """初始化策略模板"""
        try:
            templates = [
                StrategyTemplate(
                    name="动量策略模板",
                    description="基于价格动量的策略模板",
                    category="momentum",
                    code_template="""
def momentum_strategy(data, lookback_period=20, threshold=0.05):
    # 计算动量指标
    returns = data['close'].pct_change(lookback_period)
    
    # 生成信号
    signals = returns > threshold
    
    return signals
                    """,
                    parameters_schema={
                        "lookback_period": {"type": "int", "default": 20, "min": 5, "max": 100},
                        "threshold": {"type": "float", "default": 0.05, "min": 0.01, "max": 0.2}
                    }
                ),
                StrategyTemplate(
                    name="均值回归策略模板",
                    description="基于价格均值回归的策略模板",
                    category="mean_reversion",
                    code_template="""
def mean_reversion_strategy(data, window=30, std_dev=2.0):
    # 计算移动平均和标准差
    ma = data['close'].rolling(window=window).mean()
    std = data['close'].rolling(window=window).std()
    
    # 计算z-score
    z_score = (data['close'] - ma) / std
    
    # 生成信号
    signals = z_score < -std_dev
    
    return signals
                    """,
                    parameters_schema={
                        "window": {"type": "int", "default": 30, "min": 10, "max": 100},
                        "std_dev": {"type": "float", "default": 2.0, "min": 1.0, "max": 5.0}
                    }
                )
            ]

            for template in templates:
                self.templates[template.name] = template

            logger.info(f"初始化了 {len(templates)} 个策略模板")

        except Exception as e:
            logger.error(f"初始化策略模板失败: {e}")

    def create_strategy(self, strategy_data: StrategyCreate) -> StrategyResponse:
        """创建新策略"""
        try:
            strategy_id = f"strategy_{uuid.uuid4().hex[:8]}"

            strategy = Strategy(
                id=strategy_id,
                name=strategy_data.name,
                description=strategy_data.description,
                category=strategy_data.category,
                author=strategy_data.author,
                parameters=strategy_data.parameters
            )

            self.strategies[strategy_id] = strategy

            logger.info(f"创建策略成功: {strategy_id}")

            return StrategyResponse(
                success=True,
                data=strategy,
                message="策略创建成功"
            )

        except Exception as e:
            logger.error(f"创建策略失败: {e}")
            return StrategyResponse(
                success=False,
                message=f"创建策略失败: {str(e)}"
            )

    def get_strategy(self, strategy_id: str) -> StrategyResponse:
        """获取策略详情"""
        try:
            if strategy_id not in self.strategies:
                return StrategyResponse(
                    success=False,
                    message=f"策略不存在: {strategy_id}"
                )

            strategy = self.strategies[strategy_id]

            return StrategyResponse(
                success=True,
                data=strategy,
                message="获取策略成功"
            )

        except Exception as e:
            logger.error(f"获取策略失败: {e}")
            return StrategyResponse(
                success=False,
                message=f"获取策略失败: {str(e)}"
            )

    def get_strategies(self, category: Optional[str] = None) -> StrategyResponse:
        """获取策略列表"""
        try:
            strategies = list(self.strategies.values())

            if category:
                strategies = [s for s in strategies if s.category == category]

            return StrategyResponse(
                success=True,
                data=strategies,
                message="获取策略列表成功"
            )

        except Exception as e:
            logger.error(f"获取策略列表失败: {e}")
            return StrategyResponse(
                success=False,
                message=f"获取策略列表失败: {str(e)}"
            )

    def update_strategy(self, strategy_id: str, update_data: StrategyUpdate) -> StrategyResponse:
        """更新策略"""
        try:
            if strategy_id not in self.strategies:
                return StrategyResponse(
                    success=False,
                    message=f"策略不存在: {strategy_id}"
                )

            strategy = self.strategies[strategy_id]

            # 更新字段
            update_dict = update_data.dict(exclude_unset=True)
            for field, value in update_dict.items():
                setattr(strategy, field, value)

            strategy.updated_at = datetime.now()

            return StrategyResponse(
                success=True,
                data=strategy,
                message="策略更新成功"
            )

        except Exception as e:
            logger.error(f"更新策略失败: {e}")
            return StrategyResponse(
                success=False,
                message=f"更新策略失败: {str(e)}"
            )

    def delete_strategy(self, strategy_id: str) -> StrategyResponse:
        """删除策略"""
        try:
            if strategy_id not in self.strategies:
                return StrategyResponse(
                    success=False,
                    message=f"策略不存在: {strategy_id}"
                )

            del self.strategies[strategy_id]

            logger.info(f"删除策略成功: {strategy_id}")

            return StrategyResponse(
                success=True,
                message="策略删除成功"
            )

        except Exception as e:
            logger.error(f"删除策略失败: {e}")
            return StrategyResponse(
                success=False,
                message=f"删除策略失败: {str(e)}"
            )

    def execute_strategy(self, execution: StrategyExecution) -> StrategyResponse:
        """执行策略"""
        try:
            if execution.strategy_id not in self.strategies:
                return StrategyResponse(
                    success=False,
                    message=f"策略不存在: {execution.strategy_id}"
                )

            execution_id = f"exec_{uuid.uuid4().hex[:8]}"

            # 创建执行记录
            result = StrategyResult(
                execution_id=execution_id,
                strategy_id=execution.strategy_id,
                status="running",
                start_time=datetime.now()
            )

            self.executions[execution_id] = result

            # 这里应该调用实际的策略执行逻辑
            # 暂时返回模拟结果
            result.status = "completed"
            result.end_time = datetime.now()
            result.results = {
                "total_return": 0.15,
                "sharpe_ratio": 1.2,
                "max_drawdown": -0.08,
                "win_rate": 0.65,
                "total_trades": 45
            }

            logger.info(f"策略执行完成: {execution_id}")

            return StrategyResponse(
                success=True,
                data=result,
                message="策略执行完成"
            )

        except Exception as e:
            logger.error(f"策略执行失败: {e}")
            return StrategyResponse(
                success=False,
                message=f"策略执行失败: {str(e)}"
            )

    def get_execution_result(self, execution_id: str) -> StrategyResponse:
        """获取执行结果"""
        try:
            if execution_id not in self.executions:
                return StrategyResponse(
                    success=False,
                    message=f"执行记录不存在: {execution_id}"
                )

            result = self.executions[execution_id]

            return StrategyResponse(
                success=True,
                data=result,
                message="获取执行结果成功"
            )

        except Exception as e:
            logger.error(f"获取执行结果失败: {e}")
            return StrategyResponse(
                success=False,
                message=f"获取执行结果失败: {str(e)}"
            )

    def get_templates(self, category: Optional[str] = None) -> StrategyResponse:
        """获取策略模板"""
        try:
            templates = list(self.templates.values())

            if category:
                templates = [t for t in templates if t.category == category]

            return StrategyResponse(
                success=True,
                data=templates,
                message="获取策略模板成功"
            )

        except Exception as e:
            logger.error(f"获取策略模板失败: {e}")
            return StrategyResponse(
                success=False,
                message=f"获取策略模板失败: {str(e)}"
            )

    def get_strategy_statistics(self) -> StrategyResponse:
        """获取策略统计信息"""
        try:
            total_strategies = len(self.strategies)
            active_strategies = len(
                [s for s in self.strategies.values() if s.status == "active"])
            total_executions = len(self.executions)

            category_stats = {}
            for strategy in self.strategies.values():
                category = strategy.category
                if category not in category_stats:
                    category_stats[category] = 0
                category_stats[category] += 1

            statistics = {
                "total_strategies": total_strategies,
                "active_strategies": active_strategies,
                "total_executions": total_executions,
                "category_distribution": category_stats
            }

            return StrategyResponse(
                success=True,
                data=statistics,
                message="获取统计信息成功"
            )

        except Exception as e:
            logger.error(f"获取统计信息失败: {e}")
            return StrategyResponse(
                success=False,
                message=f"获取统计信息失败: {str(e)}"
            )


# 全局服务实例
strategy_service = StrategyService()
