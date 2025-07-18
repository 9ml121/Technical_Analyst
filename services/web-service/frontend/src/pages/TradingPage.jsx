/**
 * 模拟实盘交易页面
 */

import React, { useState, useEffect } from 'react';
import { Row, Col, Card, Statistic, Button, Table, Tag, message, Spin } from 'antd';
import { PlayCircleOutlined, PauseCircleOutlined, StopOutlined } from '@ant-design/icons';
import { TradingAPI } from '../services/api';
import './TradingPage.css';

const TradingPage = () => {
  const [loading, setLoading] = useState(true);
  const [accountSummary, setAccountSummary] = useState({
    total_asset: 105000,
    today_profit: 1200,
    today_return_rate: 1.2,
    position_count: 3,
    win_rate: 65.7
  });
  const [positions, setPositions] = useState([]);
  const [marketData, setMarketData] = useState({
    indices: []
  });
  const [strategies, setStrategies] = useState([]);

  // 加载初始数据
  useEffect(() => {
    loadInitialData();
    
    // 启动实时数据更新
    const cleanupFn = TradingAPI.startRealtimeUpdates(handleRealtimeUpdate);
    
    // 组件卸载时清理
    return () => {
      cleanupFn();
    };
  }, []);
  
  // 加载初始数据
  const loadInitialData = async () => {
    try {
      setLoading(true);
      const [summary, positionsData, strategiesData] = await Promise.all([
        TradingAPI.getAccountSummary(),
        TradingAPI.getPositions(),
        TradingAPI.getStrategies()
      ]);
      
      setAccountSummary(summary);
      setPositions(positionsData.positions || positionsData);
      setStrategies(strategiesData);
    } catch (error) {
      message.error('加载数据失败');
      console.error('加载初始数据失败:', error);
    } finally {
      setLoading(false);
    }
  };

  // 处理实时数据更新
  const handleRealtimeUpdate = (data) => {
    if (data.account) {
      setAccountSummary(data.account);
    }
    if (data.market) {
      setMarketData(data.market);
    }
  };

  // 处理策略控制
  const handleStrategyControl = async (strategyId, action) => {
    try {
      let response;
      switch (action) {
        case 'start':
          response = await TradingAPI.startStrategy(strategyId);
          message.success('策略启动成功');
          break;
        case 'pause':
          response = await TradingAPI.pauseStrategy(strategyId);
          message.success('策略暂停成功');
          break;
        case 'stop':
          response = await TradingAPI.stopStrategy(strategyId);
          message.success('策略停止成功');
          break;
      }
      
      // 重新加载策略数据
      const updatedStrategies = await TradingAPI.getStrategies();
      setStrategies(updatedStrategies);
    } catch (error) {
      message.error(`策略${action}失败`);
      console.error('策略控制失败:', error);
    }
  };

  // 处理卖出持仓
  const handleSellPosition = async (symbol, quantity) => {
    try {
      await TradingAPI.createOrder({
        symbol,
        trade_type: 'sell',
        quantity,
        order_type: 'market'
      });
      message.success(`成功提交卖出订单: ${symbol}`);
      
      // 重新加载持仓数据
      const updatedPositions = await TradingAPI.getPositions();
      setPositions(updatedPositions.positions || updatedPositions);
    } catch (error) {
      message.error('卖出失败');
      console.error('卖出持仓失败:', error);
    }
  };

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '50px' }}>
        <Spin size="large" />
        <p>加载中...</p>
      </div>
    );
  }

  return (
    <div className="trading-page">
      {/* 账户资产概览 */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col span={6}>
          <Card>
            <Statistic
              title="总资产"
              value={accountSummary?.total_asset || 0}
              precision={2}
              prefix="¥"
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="今日盈亏"
              value={accountSummary?.today_profit || 0}
              precision={2}
              prefix={accountSummary?.today_profit >= 0 ? '+¥' : '-¥'}
              valueStyle={{ color: accountSummary?.today_profit >= 0 ? '#52c41a' : '#ff4d4f' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="持仓数量"
              value={accountSummary?.position_count || 0}
              suffix="只"
              valueStyle={{ color: '#722ed1' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="胜率"
              value={accountSummary?.win_rate || 0}
              precision={1}
              suffix="%"
              valueStyle={{ color: '#fa8c16' }}
            />
          </Card>
        </Col>
      </Row>

      {/* 市场指数概览 */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col span={24}>
          <Card title="市场指数" size="small">
            <Row gutter={16}>
              {marketData?.indices?.map((index, i) => (
                <Col span={6} key={i}>
                  <div style={{ textAlign: 'center' }}>
                    <div style={{ fontSize: '14px', color: '#666' }}>{index.name}</div>
                    <div style={{ fontSize: '18px', fontWeight: 'bold' }}>{index.current}</div>
                    <div style={{ 
                      fontSize: '12px', 
                      color: index.change >= 0 ? '#52c41a' : '#ff4d4f' 
                    }}>
                      {index.change >= 0 ? '+' : ''}{index.change} ({index.change_percent}%)
                    </div>
                  </div>
                </Col>
              ))}
            </Row>
          </Card>
        </Col>
      </Row>

      {/* 策略控制面板 */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col span={24}>
          <Card title="策略控制" size="small">
            <Row gutter={16}>
              {strategies?.map((strategy) => (
                <Col span={8} key={strategy.id}>
                  <Card size="small">
                    <div style={{ marginBottom: 8 }}>
                      <strong>{strategy.name}</strong>
                      <Tag 
                        color={strategy.status === 'running' ? 'green' : 'orange'}
                        style={{ marginLeft: 8 }}
                      >
                        {strategy.status === 'running' ? '运行中' : '已停止'}
                      </Tag>
                    </div>
                    <div style={{ textAlign: 'center' }}>
                      <Button 
                        type="primary" 
                        icon={<PlayCircleOutlined />}
                        size="small"
                        style={{ marginRight: 8 }}
                        onClick={() => handleStrategyControl(strategy.id, 'start')}
                        disabled={strategy.status === 'running'}
                      >
                        启动
                      </Button>
                      <Button 
                        icon={<PauseCircleOutlined />}
                        size="small"
                        style={{ marginRight: 8 }}
                        onClick={() => handleStrategyControl(strategy.id, 'pause')}
                        disabled={strategy.status !== 'running'}
                      >
                        暂停
                      </Button>
                      <Button 
                        danger
                        icon={<StopOutlined />}
                        size="small"
                        onClick={() => handleStrategyControl(strategy.id, 'stop')}
                        disabled={strategy.status !== 'running'}
                      >
                        停止
                      </Button>
                    </div>
                  </Card>
                </Col>
              ))}
            </Row>
          </Card>
        </Col>
      </Row>

      {/* 持仓信息 */}
      <Card title="当前持仓" size="small">
        <Table
          dataSource={positions}
          size="small"
          pagination={false}
          rowKey="symbol"
          columns={[
            {
              title: '股票代码',
              dataIndex: 'symbol',
              key: 'symbol',
            },
            {
              title: '股票名称',
              dataIndex: 'symbol_name',
              key: 'symbol_name',
            },
            {
              title: '持仓数量',
              dataIndex: 'quantity',
              key: 'quantity',
            },
            {
              title: '成本价',
              dataIndex: 'avg_cost',
              key: 'avg_cost',
              render: (val) => `¥${val}`
            },
            {
              title: '现价',
              dataIndex: 'current_price',
              key: 'current_price',
              render: (val) => `¥${val}`
            },
            {
              title: '市值',
              dataIndex: 'market_value',
              key: 'market_value',
              render: (val) => `¥${val}`
            },
            {
              title: '浮动盈亏',
              dataIndex: 'unrealized_pnl',
              key: 'unrealized_pnl',
              render: (val, record) => (
                <span style={{ color: val >= 0 ? '#52c41a' : '#ff4d4f' }}>
                  {val >= 0 ? '+' : ''}¥{val} ({record.unrealized_pnl_rate}%)
                </span>
              )
            },
            {
              title: '操作',
              key: 'action',
              render: (_, record) => (
                <Button 
                  type="primary" 
                  danger 
                  size="small"
                  onClick={() => handleSellPosition(record.symbol, record.quantity)}
                >
                  卖出
                </Button>
              )
            }
          ]}
        />
      </Card>
    </div>
  );
};

export default TradingPage;
