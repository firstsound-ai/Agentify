import React, { useState, useEffect, useRef } from "react";
import mermaid from "mermaid";

const DynamicFlowchart = ({ code }) => {
  const [flowchartCode, setFlowchartCode] = useState(
    code ||
      `flowchart TD
    A[Christmas] -->|Get money| B(Go shopping)
    B --> C{Let me think}
    C -->|One| D[Laptop]
    C -->|Two| E[iPhone]
    C -->|Three| F[fa:fa-car Car]
    `,
  );

  const mermaidRef = useRef(null);
  const [isInitialized, setIsInitialized] = useState(false);

  useEffect(() => {
    if (!isInitialized) {
      mermaid.initialize({
        startOnLoad: false,
        theme: "default",
        securityLevel: "loose",
        fontFamily: "Arial, sans-serif",
      });
      setIsInitialized(true);
    }
  }, [isInitialized]);

  useEffect(() => {
    if (code && code !== flowchartCode) {
      setFlowchartCode(code);
    }
  }, [code]);

  // 渲染Mermaid图表
  useEffect(() => {
    if (!isInitialized || !flowchartCode || !mermaidRef.current) {
      return;
    }

    const renderMermaid = async () => {
      try {
        mermaidRef.current.innerHTML = "";

        // 添加一个小延迟确保DOM更新完成
        await new Promise((resolve) => setTimeout(resolve, 100));

        const graphId = `mermaid-${Date.now()}-${Math.random()
          .toString(36)
          .substr(2, 9)}`;

        const { svg } = await mermaid.render(graphId, flowchartCode);

        if (mermaidRef.current) {
          mermaidRef.current.innerHTML = svg;
        }
      } catch (error) {
        console.error("Mermaid渲染错误:", error);
        if (mermaidRef.current) {
          mermaidRef.current.innerHTML = `<div style="color: red; padding: 20px;">流程图渲染失败: ${error.message}</div>`;
        }
      }
    };

    renderMermaid();
  }, [isInitialized, flowchartCode]);

  return (
    <div
      ref={mermaidRef}
      className="mermaid-container"
      style={{
        minHeight: "200px",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
      }}
    >
      {!isInitialized && <div>正在初始化图表...</div>}
    </div>
  );
};

export default DynamicFlowchart;
