import React from 'react';
import { ConfigProvider } from 'antd';
import zhCN from 'antd/locale/zh_CN';
import TradingPage from './pages/TradingPage';
import './App.css';

function App() {
  return (
    <ConfigProvider locale={zhCN}>
      <div className="App">
        <header className="app-header">
          <h1>Technical_Analyst - 模拟实盘交易</h1>
        </header>
        <main>
          <TradingPage />
        </main>
      </div>
    </ConfigProvider>
  );
}

export default App;
