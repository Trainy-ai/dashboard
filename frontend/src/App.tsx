// @ts-nocheck

import { useState } from 'react'
import { Layout } from "antd";
import TopicMenu from "./components/TopicMenu.jsx";
import SideBar from "./components/SideBar/SideBar.jsx";
import KernelView from "./components/KernelView/KernelView.tsx";
import ProgressView from "./components/ProgressView/ProgressView.jsx";
import ConsistencyView from './components/ConsistencyView/ConsistencyView.tsx';
import CompCommOverlapView from './components/CompCommOverlapView/CompCommOverlapView.tsx';
import UtilView from './components/UtilView/UtilView.js';
import TemporalView from './components/TemporalView/TemporalView.js';
import IdleTimeView from './components/IdleTimeView/IdleTimeView.js';
import './App.css'


function App() {
  const topics = ["Temporal", "Kernels", "Computation/Communication Overlap", "Progress", "Consistency", "GPU Util", "Idle Time"];
  const [contentIndex, setContentIndex] = useState(0);
  const [traceFolder, setTraceFolder] = useState('');

  const changeSelectedKey = (event) => {
    const key = event.key;
    setContentIndex(key);
  };

  const Menu = (
    <TopicMenu
      topics={topics}
      selectedKey={String(contentIndex)}
      changeSelectedKey={changeSelectedKey}
    />
  );

  let plot;
  if (contentIndex == 0) {
    plot = <TemporalView traceFolder={traceFolder} />
  } else if (contentIndex == 1) {
    plot = <KernelView traceFolder={traceFolder} />
  } else if (contentIndex == 2) {
    plot = <CompCommOverlapView traceFolder={traceFolder} />
  } else if (contentIndex == 3) {
    plot = <ProgressView traceFolder={traceFolder} />
  } else if (contentIndex == 4) {
    plot = <ConsistencyView traceFolder={traceFolder} />
  } else if (contentIndex == 5) {
    plot = <UtilView traceFolder={traceFolder} />
  } else {
    plot = <IdleTimeView traceFolder={traceFolder} />
  }

  console.log('render app')

  return (
    <div className="App">
      <Layout>
        <SideBar menu={Menu} traceFolder={traceFolder} setTraceFolder={setTraceFolder} />
        <Layout.Content className="content">
          {plot}
        </Layout.Content>
      </Layout>
    </div>
  );
}

export default App
