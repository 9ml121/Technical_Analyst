import React from 'react';
import { ConfigProvider } from 'antd';
import zhCN from 'antd/locale/zh_CN';
import TradingPageSimple from './pages/TradingPageSimple';
import './App.css';

function App() {
  return (
    <ConfigProvider locale={zhCN}>
      <div className="App">
        <header className="app-header">
          <h1>Technical_Analyst - 模拟实盘交易</h1>
        </header>
        <main>
          <div style={{ padding: '20px' }}>
            <TradingPageSimple />
          </div>
        </main>
      </div>
    </ConfigProvider>
  );
}

export default App;
