/**
 * 简化版模拟实盘交易页面
 */

import React, { useState, useEffect } from 'react';
import { Row, Col, Card, Statistic, Button, Table, Tag, message, Spin } from 'antd';
import { PlayCircleOutlined, PauseCircleOutlined, StopOutlined } from '@ant-design/icons';
import tradingAPI from '../services/tradingApi';

const TradingPageSimple = () => {
  const [loading, setLoading] = useState(true);
  const [accountSummary, setAccountSummary] = useState(null);
  const [positions, setPositions] = useState([]);
  const [marketData, setMarketData] = useState(null);
  const [strategies, setStrategies] = useState([]);
  const [realtimeCleanup, setRealtimeCleanup] = useState(null);

  // 初始化数据加载
  useEffect(() => {
    loadInitialData();

    // 启动实时数据更新
    const cleanup = tradingAPI.startRealtimeUpdates(handleRealtimeUpdate, 2000);
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
        tradingAPI.getAccountSummary(),
        tradingAPI.getPositions(),
        tradingAPI.getStrategies()
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
          response = await tradingAPI.startStrategy(strategyId);
          message.success('策略启动成功');
          break;
        case 'pause':
          response = await tradingAPI.pauseStrategy(strategyId);
          message.success('策略暂停成功');
          break;
        case 'stop':
          response = await tradingAPI.stopStrategy(strategyId);
          message.success('策略停止成功');
          break;
      }

      // 重新加载策略数据
      const updatedStrategies = await tradingAPI.getStrategies();
      setStrategies(updatedStrategies);
    } catch (error) {
      message.error(`策略${action}失败`);
      console.error('策略控制失败:', error);
    }
  };

  const handleSellPosition = async (symbol, quantity) => {
    try {
      await tradingAPI.sellPosition(1, symbol, quantity);
      message.success(`成功卖出 ${symbol}`);

      // 重新加载持仓数据
      const updatedPositions = await tradingAPI.getPositions();
      setPositions(updatedPositions);

      // 重新加载账户概览
      const updatedSummary = await tradingAPI.getAccountSummary();
      setAccountSummary(updatedSummary);
    } catch (error) {
      message.error('卖出失败');
      console.error('卖出失败:', error);
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
    <div className="trading-page" style={{ padding: '20px' }}>
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
              value={Math.abs(accountSummary?.today_profit || 0)}
              precision={2}
              prefix={(accountSummary?.today_profit || 0) >= 0 ? '+¥' : '-¥'}
              valueStyle={{ color: (accountSummary?.today_profit || 0) >= 0 ? '#52c41a' : '#ff4d4f' }}
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

      {/* 大盘分析和策略控制 */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col span={12}>
          <Card title="大盘指数">
            {marketData?.indices?.length > 0 ? (
              marketData.indices.map(index => (
                <div key={index.code} style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  marginBottom: '8px',
                  padding: '8px',
                  backgroundColor: '#fafafa',
                  borderRadius: '4px'
                }}>
                  <span style={{ fontWeight: 'bold' }}>{index.name}</span>
                  <div>
                    <span style={{ marginRight: '8px' }}>{index.current?.toFixed(2)}</span>
                    <span style={{
                      color: (index.change || 0) >= 0 ? '#52c41a' : '#ff4d4f',
                      fontWeight: 'bold'
                    }}>
                      {(index.change || 0) >= 0 ? '+' : ''}{(index.change || 0).toFixed(2)}
                      ({(index.change_percent || 0) >= 0 ? '+' : ''}{(index.change_percent || 0).toFixed(2)}%)
                    </span>
                  </div>
                </div>
              ))
            ) : (
              <div style={{ textAlign: 'center', color: '#999', padding: '20px' }}>
                加载中...
              </div>
            )}
          </Card>
        </Col>
        <Col span={12}>
          <Card title="策略控制">
            {strategies.length > 0 && (
              <div>
                <div style={{ marginBottom: '16px' }}>
                  <h4 style={{ margin: 0, marginBottom: '8px' }}>{strategies[0].name} v{strategies[0].version}</h4>
                  <Tag color={
                    strategies[0].status === 'running' ? 'green' : 
                    strategies[0].status === 'paused' ? 'orange' : 'default'
                  }>
                    {strategies[0].status === 'running' ? '运行中' : 
                     strategies[0].status === 'paused' ? '已暂停' : '已停止'}
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
      <Card title="当前持仓">
        <Table
          dataSource={positions}
          rowKey="symbol"
          size="small"
          pagination={false}
          columns={[
            { title: '股票代码', dataIndex: 'symbol', key: 'symbol' },
            { title: '股票名称', dataIndex: 'symbol_name', key: 'symbol_name' },
            {
              title: '持仓数量',
              dataIndex: 'quantity',
              key: 'quantity',
              render: val => `${(val || 0).toLocaleString()}股`
            },
            {
              title: '成本价',
              dataIndex: 'avg_cost',
              key: 'avg_cost',
              render: val => `¥${(val || 0).toFixed(2)}`
            },
            {
              title: '现价',
              dataIndex: 'current_price',
              key: 'current_price',
              render: val => `¥${(val || 0).toFixed(2)}`
            },
            {
              title: '市值',
              dataIndex: 'market_value',
              key: 'market_value',
              render: val => `¥${(val || 0).toLocaleString()}`
            },
            {
              title: '盈亏',
              dataIndex: 'unrealized_pnl',
              key: 'unrealized_pnl',
              render: (val, record) => (
                <span style={{ color: (val || 0) >= 0 ? '#52c41a' : '#ff4d4f' }}>
                  {(val || 0) >= 0 ? '+' : ''}¥{(val || 0).toFixed(2)}
                  <br />
                  <small>({(record.unrealized_pnl_rate || 0).toFixed(2)}%)</small>
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

export default TradingPageSimple;
