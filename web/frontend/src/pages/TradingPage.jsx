/**
 * 模拟实盘交易页面
 */

import React, { useState, useEffect } from 'react';
import { Row, Col, Card, Statistic, Button, Table, Tag, message, Spin } from 'antd';
import { PlayCircleOutlined, PauseCircleOutlined, StopOutlined } from '@ant-design/icons';
import TradingAPI from '../services/api';
import './TradingPage.css';

const TradingPage = () => {
  const [loading, setLoading] = useState(true);
  const [accountSummary, setAccountSummary] = useState(null);
  const [positions, setPositions] = useState([]);
  const [marketData, setMarketData] = useState(null);
  const [strategies, setStrategies] = useState([]);
  const [realtimeCleanup, setRealtimeCleanup] = useState(null);

  // 初始化数据
  useEffect(() => {
    loadInitialData();
    
    // 启动实时数据更新
    const cleanup = TradingAPI.startRealtimeUpdates(handleRealtimeUpdate, 2000);
    setRealtimeCleanup(() => cleanup);
    
    // 清理函数
    return () => {
      if (cleanup) cleanup();
    };
  }, []);

  const loadInitialData = async () => {
    try {
      setLoading(true);
      const [summary, positionsData, strategiesData] = await Promise.all([
        TradingAPI.getAccountSummary(),
        TradingAPI.getPositions(),
        TradingAPI.getStrategies()
      ]);
      
      setAccountSummary(summary);
      setPositions(positionsData);
      setStrategies(strategiesData);
    } catch (error) {
      message.error('加载数据失败');
      console.error('加载初始数据失败:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleRealtimeUpdate = (data) => {
    if (data.account) {
      setAccountSummary(data.account);
    }
    if (data.market) {
      setMarketData(data.market);
    }
  };

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

  const handleSellPosition = async (symbol, quantity) => {
    try {
      await TradingAPI.sellPosition(1, symbol, quantity);
      message.success(`成功卖出 ${symbol}`);
      
      // 重新加载持仓数据
      const updatedPositions = await TradingAPI.getPositions();
      setPositions(updatedPositions);
      
      // 重新加载账户概览
      const updatedSummary = await TradingAPI.getAccountSummary();
      setAccountSummary(updatedSummary);
    } catch (error) {
      message.error('卖出失败');
      console.error('卖出失败:', error);
    }
  };

  // 持仓表格列定义
  const positionColumns = [
    {
      title: '股票代码',
      dataIndex: 'symbol',
      key: 'symbol',
      width: 100,
    },
    {
      title: '股票名称',
      dataIndex: 'symbol_name',
      key: 'symbol_name',
      width: 120,
    },
    {
      title: '持仓数量',
      dataIndex: 'quantity',
      key: 'quantity',
      width: 100,
      render: (value) => value?.toLocaleString() || 0,
    },
    {
      title: '成本价',
      dataIndex: 'avg_cost',
      key: 'avg_cost',
      width: 100,
      render: (value) => `¥${value?.toFixed(2) || '0.00'}`,
    },
    {
      title: '现价',
      dataIndex: 'current_price',
      key: 'current_price',
      width: 100,
      render: (value) => `¥${value?.toFixed(2) || '0.00'}`,
    },
    {
      title: '市值',
      dataIndex: 'market_value',
      key: 'market_value',
      width: 120,
      render: (value) => `¥${value?.toLocaleString() || '0'}`,
    },
    {
      title: '盈亏',
      dataIndex: 'unrealized_pnl',
      key: 'unrealized_pnl',
      width: 120,
      render: (value, record) => (
        <span style={{ color: value >= 0 ? '#52c41a' : '#ff4d4f' }}>
          {value >= 0 ? '+' : ''}¥{value?.toFixed(2) || '0.00'}
          <br />
          <small>({record.unrealized_pnl_rate?.toFixed(2) || '0.00'}%)</small>
        </span>
      ),
    },
    {
      title: '操作',
      key: 'action',
      width: 100,
      render: (_, record) => (
        <Button 
          type="primary" 
          danger 
          size="small"
          onClick={() => handleSellPosition(record.symbol, record.quantity)}
        >
          卖出
        </Button>
      ),
    },
  ];

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
              valueStyle={{ 
                color: accountSummary?.today_profit >= 0 ? '#52c41a' : '#ff4d4f' 
              }}
            />
            <div style={{ fontSize: '12px', color: '#666', marginTop: '4px' }}>
              ({accountSummary?.today_return_rate?.toFixed(2) || '0.00'}%)
            </div>
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
            <div style={{ fontSize: '12px', color: '#666', marginTop: '4px' }}>
              仓位: {accountSummary?.position_ratio?.toFixed(1) || '0.0'}%
            </div>
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="胜率"
              value={accountSummary?.win_rate || 0}
              precision={1}
              suffix="%"
              valueStyle={{ color: '#52c41a' }}
            />
            <div style={{ fontSize: '12px', color: '#666', marginTop: '4px' }}>
              {accountSummary?.win_trades || 0}胜/{(accountSummary?.total_trades || 0) - (accountSummary?.win_trades || 0)}负
            </div>
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]}>
        {/* 大盘分析 */}
        <Col span={12}>
          <Card title="大盘分析" size="small">
            {marketData && (
              <Row gutter={[8, 8]}>
                {marketData.indices?.map((index) => (
                  <Col span={12} key={index.code}>
                    <div style={{ 
                      padding: '8px', 
                      border: '1px solid #f0f0f0', 
                      borderRadius: '4px',
                      textAlign: 'center'
                    }}>
                      <div style={{ fontSize: '12px', color: '#666' }}>{index.name}</div>
                      <div style={{ fontSize: '16px', fontWeight: 'bold' }}>
                        {index.current?.toFixed(2)}
                      </div>
                      <div style={{ 
                        fontSize: '12px', 
                        color: index.change_percent >= 0 ? '#52c41a' : '#ff4d4f' 
                      }}>
                        {index.change_percent >= 0 ? '+' : ''}{index.change_percent?.toFixed(2)}%
                      </div>
                    </div>
                  </Col>
                ))}
              </Row>
            )}
          </Card>
        </Col>

        {/* 策略控制 */}
        <Col span={12}>
          <Card title="策略控制" size="small">
            {strategies.length > 0 && (
              <div>
                <div style={{ marginBottom: '12px' }}>
                  <strong>{strategies[0].name}</strong> v{strategies[0].version}
                  <Tag 
                    color={strategies[0].status === 'running' ? 'green' : 'default'}
                    style={{ marginLeft: '8px' }}
                  >
                    {strategies[0].status === 'running' ? '运行中' : '已停止'}
                  </Tag>
                </div>
                <div>
                  <Button
                    type="primary"
                    icon={<PlayCircleOutlined />}
                    size="small"
                    style={{ marginRight: '8px' }}
                    disabled={strategies[0].status === 'running'}
                    onClick={() => handleStrategyControl(strategies[0].id, 'start')}
                  >
                    启动
                  </Button>
                  <Button
                    icon={<PauseCircleOutlined />}
                    size="small"
                    style={{ marginRight: '8px' }}
                    disabled={strategies[0].status !== 'running'}
                    onClick={() => handleStrategyControl(strategies[0].id, 'pause')}
                  >
                    暂停
                  </Button>
                  <Button
                    danger
                    icon={<StopOutlined />}
                    size="small"
                    disabled={strategies[0].status === 'stopped'}
                    onClick={() => handleStrategyControl(strategies[0].id, 'stop')}
                  >
                    停止
                  </Button>
                </div>
              </div>
            )}
          </Card>
        </Col>
      </Row>

      {/* 持仓列表 */}
      <Card title="当前持仓" style={{ marginTop: 16 }}>
        <Table
          columns={positionColumns}
          dataSource={positions}
          rowKey="symbol"
          size="small"
          pagination={false}
          locale={{ emptyText: '暂无持仓' }}
        />
      </Card>
    </div>
  );
};

export default TradingPage;
