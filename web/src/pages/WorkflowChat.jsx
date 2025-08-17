import { useState, useEffect, useRef, useCallback } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import {
  Layout,
  Button,
  Typography,
  Card,
  Spin,
  Progress,
  Tabs,
  TabPane,
  Chat,
} from "@douyinfe/semi-ui";
import { IconArrowLeft, IconCode, IconBranch } from "@douyinfe/semi-icons";
import request from "../utils/request";
import "./WorkflowChat.css";
import DynamicFlowchart from "../components/DynamicFlowchart";

const { Content } = Layout;
const { Title, Text } = Typography;

function Workflow() {
  const navigate = useNavigate();
  const location = useLocation();
  const threadId = location.state?.threadId || "123";
  const blueprintId = location.state?.blueprintId || "";
  const formData = location.state?.formData || {};
  const userInput = location.state?.userInput || "";

  const [isLoading, setIsLoading] = useState(true);
  const [progress, setProgress] = useState(0);
  const [currentStep, setCurrentStep] = useState("");
  const [workflowData, setWorkflowData] = useState(null);
  const [blueprintStatus, setBlueprintStatus] = useState("pending");
  const [mermaidCode, setMermaidCode] = useState("");
  const [isWorkflowLoading, setIsWorkflowLoading] = useState(false); // 动态工作流加载状态
  const pollingRef = useRef(null);
  const workflowPollingRef = useRef(null); // 用于聊天后的工作流轮询
  const [messages, setMessages] = useState([]);
  const [isAiTyping, setIsAiTyping] = useState(false);
  const messageIdRef = useRef(3);
  const currentSSEController = useRef(null); 

  // 初始化AI欢迎消息
  const initializeWelcomeMessage = useCallback((stepCount) => {
    const welcomeMessage = {
      role: "assistant",
      id: "1",
      createAt: Date.now(),
      content: `根据您的需求，我为您草拟了一份包含 ${
        stepCount || 0
      } 个步骤的工作流程，您可以在左侧查看完整流程和流程图。如果您需要继续修改，可以通过聊天来修改您的工作流。`,
      status: "complete",
    };
    setMessages([welcomeMessage]);
  }, []);

  // 初始化时显示欢迎消息
  useEffect(() => {
    if (messages.length === 0) {
      initializeWelcomeMessage(0);
    }
  }, [initializeWelcomeMessage, messages.length]);

  // 处理用户发送消息
  const handleMessageSend = useCallback((content, attachment) => {
    setIsAiTyping(true);
    setIsWorkflowLoading(true); // 开始时就设置工作流为加载状态
    
    // 创建AI响应消息（先显示加载状态）
    const aiMessageId = String(messageIdRef.current++);
    const aiResponseLoading = {
      role: 'assistant',
      id: aiMessageId,
      createAt: Date.now(),
      content: '',
      status: 'loading'
    };
    
    // 添加AI加载消息
    setTimeout(() => {
      setMessages(prev => [...prev, aiResponseLoading]);
    }, 100);
    
    // 发送SSE请求
    sendChatMessageSSE(content, aiMessageId);
  }, [threadId]);

  // SSE聊天请求函数
  const sendChatMessageSSE = useCallback(async (content, messageId) => {
    try {
      // 取消之前的请求
      if (currentSSEController.current) {
        currentSSEController.current.abort();
      }

      // 创建新的AbortController
      const controller = new AbortController();
      currentSSEController.current = controller;

      const response = await fetch(`/api/blueprint/chat/completions/${threadId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'text/event-stream',
        },
        body: JSON.stringify({
          prompt: content
        }),
        signal: controller.signal, // 添加取消信号
      });

      if (!response.ok) {
        throw new Error(`网络请求失败: ${response.status} ${response.statusText}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      while (true) {
        const { done, value } = await reader.read();
        
        if (done) {
          // 流结束，设置完成状态
          setMessages(prev => prev.map(msg => 
            msg.id === messageId 
              ? { ...msg, status: 'complete' }
              : msg
          ));
          setIsAiTyping(false);
          currentSSEController.current = null;
          
          // 启动工作流更新轮询（加载状态已在发送消息时设置）
          workflowPollingRef.current = setInterval(() => {
            pollWorkflowUpdates();
          }, 3000);
          
          break;
        }

        const chunk = decoder.decode(value, { stream: true });
        
        // 使用正则表达式匹配所有的data块，包括在同一行的多个块
        const dataMatches = chunk.match(/data:\s*\{[^}]*\}/g) || [];
        
        for (const match of dataMatches) {
          // 提取JSON部分（去掉"data: "前缀）
          const jsonStr = match.replace(/^data:\s*/, '').trim();
          
          // 检查是否是结束标记
          if (jsonStr === '[DONE]') {
            setMessages(prev => prev.map(msg => 
              msg.id === messageId 
                ? { ...msg, status: 'complete' }
                : msg
            ));
            setIsAiTyping(false);
            currentSSEController.current = null;
            
            // 启动工作流更新轮询（加载状态已在发送消息时设置）
            workflowPollingRef.current = setInterval(() => {
              pollWorkflowUpdates();
            }, 3000);
            
            return;
          }
          
          try {
            const parsed = JSON.parse(jsonStr);
            let contentToAdd = '';
            
            // 支持你的后端格式：{"chunk": "文本"}
            if (parsed.chunk !== undefined) {
              contentToAdd = parsed.chunk;
            }
            // 支持OpenAI格式
            else if (parsed.choices && parsed.choices[0] && parsed.choices[0].delta && parsed.choices[0].delta.content) {
              contentToAdd = parsed.choices[0].delta.content;
            }
            // 支持简单的content字段
            else if (parsed.content !== undefined) {
              contentToAdd = parsed.content;
            }
            
            if (contentToAdd) {
              setMessages(prev => prev.map(msg => {
                if (msg.id === messageId) {
                  return { 
                    ...msg, 
                    content: (msg.content || '') + contentToAdd, 
                    status: 'incomplete' 
                  };
                }
                return msg;
              }));
            }
            
          } catch (e) {
            console.debug('SSE数据解析失败:', e.message, 'JSON字符串:', jsonStr);
          }
        }
      }
    } catch (error) {
      console.error('SSE请求失败:', error);
      
      // 如果是主动取消的请求，不显示错误
      if (error.name === 'AbortError') {
        console.log('SSE请求被取消');
        setIsWorkflowLoading(false); // 取消请求时清除工作流加载状态
        return;
      }
      
      // 显示错误消息
      setMessages(prev => prev.map(msg => 
        msg.id === messageId 
          ? { 
              ...msg, 
              content: '抱歉，处理您的消息时出现了问题，请稍后重试。\n错误信息: ' + error.message, 
              status: 'error' 
            }
          : msg
      ));
      setIsAiTyping(false);
      setIsWorkflowLoading(false); // 出错时清除工作流加载状态
      currentSSEController.current = null;
    }
  }, [threadId]);

  // 处理消息变化
  const handleChatsChange = useCallback((chats) => {
    setMessages(chats);
  }, []);

  // 解析工作流数据，生成有序的步骤列表
  const parseWorkflowSteps = useCallback((workflowData) => {
    if (!workflowData || !workflowData.nodes || !workflowData.startNodeId) {
      return [];
    }

    const { nodes, startNodeId } = workflowData;
    const steps = [];
    const visited = new Set();
    const nodeOrder = new Map(); // 用于记录节点的遍历顺序
    let globalStepNumber = 1;

    // 广度优先遍历，确保所有节点都被访问
    const traverseAllNodes = () => {
      const queue = [{ nodeId: startNodeId, stepNumber: globalStepNumber }];

      while (queue.length > 0) {
        const { nodeId, stepNumber } = queue.shift();

        if (!nodeId || visited.has(nodeId) || !nodes[nodeId]) {
          continue;
        }

        visited.add(nodeId);
        const node = nodes[nodeId];

        // 根据节点类型确定步骤类型和图标
        let stepType = "input";
        let typeText = "输入";

        switch (node.nodeType) {
          case "TRIGGER_USER_INPUT":
            stepType = "input";
            typeText = "输入";
            break;
          case "ACTION_WEB_SEARCH":
            stepType = "search";
            typeText = "搜索";
            break;
          case "ACTION_LLM_TRANSFORM":
            stepType = "ai_processing";
            typeText = "AI处理";
            break;
          case "CONDITION_BRANCH":
            stepType = "validation";
            typeText = "判断";
            break;
          case "LOOP_START":
            stepType = "loop";
            typeText = "循环开始";
            break;
          case "LOOP_END":
            stepType = "loop";
            typeText = "循环结束";
            break;
          case "OUTPUT_FORMAT":
            stepType = "output";
            typeText = "输出";
            break;
          default:
            stepType = "ai_processing";
            typeText = "处理";
        }

        // 创建步骤对象
        const step = {
          id: nodeId,
          stepNumber: stepNumber,
          name: node.nodeTitle,
          description: node.nodeDescription || `执行${node.nodeTitle}操作`,
          type: stepType,
          typeText: typeText,
          nodeType: node.nodeType,
          edges: node.edges || [],
        };

        steps.push(step);
        nodeOrder.set(nodeId, stepNumber);
        globalStepNumber++;

        // 将所有子节点加入队列
        if (node.edges && node.edges.length > 0) {
          node.edges.forEach((edge) => {
            if (edge.targetNodeId && !visited.has(edge.targetNodeId)) {
              queue.push({
                nodeId: edge.targetNodeId,
                stepNumber: globalStepNumber,
              });
            }
          });
        }
      }
    };

    // 首先执行广度优先遍历，确保所有节点都被访问
    traverseAllNodes();

    // 然后基于主流程重新分配步骤编号
    const reassignStepNumbers = () => {
      const mainPath = [];
      const visited = new Set();

      // 追踪主路径
      const traceMainPath = (nodeId) => {
        if (!nodeId || visited.has(nodeId) || !nodes[nodeId]) {
          return;
        }

        visited.add(nodeId);
        mainPath.push(nodeId);
        const node = nodes[nodeId];

        if (node.edges && node.edges.length > 0) {
          // 优先选择主路径
          let nextEdge = null;

          if (node.nodeType === "CONDITION_BRANCH") {
            // 对于条件分支，优先选择 onSuccess 路径
            nextEdge =
              node.edges.find((edge) => edge.sourceHandle === "onSuccess") ||
              node.edges[0];
          } else if (node.nodeType === "LOOP_END") {
            // 对于循环结束，选择 onComplete 路径
            nextEdge =
              node.edges.find((edge) => edge.sourceHandle === "onComplete") ||
              node.edges[0];
          } else {
            // 对于其他节点，选择默认路径
            nextEdge =
              node.edges.find((edge) => edge.sourceHandle === "default") ||
              node.edges[0];
          }

          if (nextEdge && nextEdge.targetNodeId) {
            traceMainPath(nextEdge.targetNodeId);
          }
        }
      };

      traceMainPath(startNodeId);

      // 重新分配步骤编号
      let mainPathIndex = 1;
      let sidePathIndex = mainPath.length + 1;

      steps.forEach((step) => {
        const mainPathPosition = mainPath.indexOf(step.id);
        if (mainPathPosition !== -1) {
          step.stepNumber = mainPathPosition + 1;
          step.isMainPath = true;
        } else {
          step.stepNumber = sidePathIndex++;
          step.isMainPath = false;
        }
      });
    };

    // 重新分配步骤编号
    reassignStepNumbers();

    // 按步骤编号排序
    return steps.sort((a, b) => a.stepNumber - b.stepNumber);
  }, []);

  // 轮询蓝图状态
  const pollBlueprintStatus = useCallback(async () => {
    try {
      const result = await request.get(`/api/blueprint/latest/${threadId}`);

      if (result.code === 0 && result.data) {
        const latestBlueprint = result.data;
        
        // 更新蓝图状态
        setBlueprintStatus(latestBlueprint.status);

        if (latestBlueprint.status === "completed" && latestBlueprint.workflow) {
          // 蓝图准备完成，直接处理工作流数据
          const workflowInfo = latestBlueprint.workflow;
          const parsedSteps = parseWorkflowSteps(workflowInfo);

          const newWorkflowData = {
            name: workflowInfo.workflowName || formData.requirement_name || "智能工作流",
            workflowId: workflowInfo.workflowId,
            steps: parsedSteps,
            rawData: workflowInfo,
          };

          setWorkflowData(newWorkflowData);
          setMermaidCode(latestBlueprint.mermaid_code || "");
          setIsLoading(false);
          setProgress(100);
          setCurrentStep("工作流创建完成！");

          // 初始化AI欢迎消息
          initializeWelcomeMessage(parsedSteps.length);
          
          // 停止轮询
          if (pollingRef.current) {
            clearInterval(pollingRef.current);
            pollingRef.current = null;
          }
        }
      } else {
        console.warn("获取最新蓝图数据格式不正确:", result);
      }
    } catch (error) {
      console.error("轮询蓝图状态失败:", error);
    }
  }, [threadId, formData.requirement_name, parseWorkflowSteps, initializeWelcomeMessage]);

  // 聊天后轮询工作流更新
  const pollWorkflowUpdates = useCallback(async () => {
    try {
      const result = await request.get(`/api/blueprint/latest/${threadId}`);

      if (result.code === 0 && result.data && result.data.status === "completed" && result.data.workflow) {
        const latestBlueprint = result.data;
        const workflowInfo = latestBlueprint.workflow;
        const parsedSteps = parseWorkflowSteps(workflowInfo);

        const newWorkflowData = {
          name: workflowInfo.workflowName || formData.requirement_name || "智能工作流",
          workflowId: workflowInfo.workflowId,
          steps: parsedSteps,
          rawData: workflowInfo,
        };

        setWorkflowData(newWorkflowData);
        setMermaidCode(latestBlueprint.mermaid_code || "");
        setIsWorkflowLoading(false);
        
        // 停止轮询
        if (workflowPollingRef.current) {
          clearInterval(workflowPollingRef.current);
          workflowPollingRef.current = null;
        }
      }
    } catch (error) {
      console.error("轮询工作流更新失败:", error);
    }
  }, [threadId, formData.requirement_name, parseWorkflowSteps]);

  // 修改工作流创建过程，改为轮询蓝图状态
  useEffect(() => {
    if (!blueprintId) {
      console.error("缺少蓝图ID");
      setIsLoading(false);
      return;
    }

    // 开始轮询蓝图状态
    const startPolling = () => {
      setCurrentStep("正在生成工作流蓝图...");
      setProgress(20);

      // 立即执行一次
      pollBlueprintStatus();

      // 设置定时轮询，每3秒查询一次
      pollingRef.current = setInterval(() => {
        pollBlueprintStatus();

        // 模拟进度增长
        setProgress((prev) => {
          if (prev < 80) {
            return prev + Math.random() * 10;
          }
          return prev;
        });
      }, 3000);
    };

    // 清理函数
    const cleanup = () => {
      if (pollingRef.current) {
        clearInterval(pollingRef.current);
        pollingRef.current = null;
      }
      
      // 清理工作流轮询
      if (workflowPollingRef.current) {
        clearInterval(workflowPollingRef.current);
        workflowPollingRef.current = null;
      }
      
      // 清理SSE连接
      if (currentSSEController.current) {
        currentSSEController.current.abort();
        currentSSEController.current = null;
      }
    };

    startPolling();

    // 组件卸载时清理定时器
    return cleanup;
  }, [blueprintId, pollBlueprintStatus]);

  if (!threadId || !blueprintId) {
    return (
      <Content className="workflow-page-content">
        <div className="workflow-page-container">
          <Card className="workflow-loading-card">
            <div className="workflow-error-content">
              <Title
                heading={2}
                style={{ textAlign: "center", color: "#1a202c" }}
              >
                数据加载失败
              </Title>
              <Text
                style={{
                  textAlign: "center",
                  fontSize: "16px",
                  color: "#666",
                  marginBottom: "24px",
                }}
              >
                无法获取工作流数据，请返回重试
              </Text>
              <div style={{ textAlign: "center" }}>
                <Button onClick={() => navigate("/")} type="primary">
                  返回首页
                </Button>
              </div>
            </div>
          </Card>
        </div>
      </Content>
    );
  }

  // 加载状态
  if (isLoading) {
    return (
      <Content className="workflow-page-content">
        <div className="workflow-page-container">
          <div className="workflow-page-header">
            <Button
              icon={<IconArrowLeft />}
              theme="borderless"
              onClick={() =>
                navigate("/requirement-form", {
                  state: {
                    threadId,
                    requirementData: formData,
                    userInput,
                  },
                })
              }
              className="workflow-back-button"
            >
              返回需求确认
            </Button>

            <div className="workflow-header-info">
              <Title heading={2} style={{ margin: 0, color: "#1a202c" }}>
                正在创建工作流
              </Title>
              <Text
                type="secondary"
                style={{ marginTop: "8px", display: "block" }}
              >
                基于您的需求，我们正在为您构建智能工作流
              </Text>
            </div>
          </div>

          <Card className="workflow-loading-card">
            <div className="workflow-loading-content">
              <div className="workflow-loading-animation">
                <Spin size="large" />
              </div>

              <div className="workflow-progress-section">
                <Title
                  heading={3}
                  style={{
                    textAlign: "center",
                    margin: "32px 0 24px",
                    color: "#1a202c",
                  }}
                >
                  正在创建工作流蓝图
                </Title>

                <div className="workflow-progress-container">
                  <Progress
                    percent={progress}
                    showInfo={true}
                    stroke="#374151"
                    size="large"
                    style={{ marginBottom: "16px" }}
                  />
                  <Text
                    style={{
                      textAlign: "center",
                      fontSize: "16px",
                      color: "#666",
                      display: "block",
                      minHeight: "24px",
                    }}
                  >
                    {currentStep}
                  </Text>

                  {/* 显示蓝图状态 */}
                  <div style={{ textAlign: "center", marginTop: "12px" }}>
                    <Text style={{ fontSize: "14px", color: "#888" }}>
                      蓝图状态:{" "}
                      {blueprintStatus === "pending"
                        ? "处理中"
                        : blueprintStatus === "completed"
                          ? "已完成"
                          : blueprintStatus || "未知"}
                    </Text>
                  </div>
                </div>
              </div>

              <div className="workflow-requirement-summary">
                <Text
                  type="secondary"
                  style={{
                    fontSize: "14px",
                    textAlign: "center",
                    display: "block",
                  }}
                >
                  正在为 "{formData.requirement_name || "您的需求"}"
                  创建智能工作流
                </Text>
              </div>
            </div>
          </Card>
        </div>
      </Content>
    );
  }

  // 工作流展示 - 左右布局
  return (
    <Content className="workflow-page-content">
      <div className="workflow-page-container">
        <div className="workflow-page-header">
          <Button
            icon={<IconArrowLeft />}
            theme="borderless"
            onClick={() =>
              navigate("/requirement-form", {
                state: {
                  threadId,
                  requirementData: formData,
                  userInput,
                },
              })
            }
            className="workflow-back-button"
          >
            返回需求确认
          </Button>

          <div className="workflow-header-info">
            <Title heading={2} style={{ margin: 0, color: "#1a202c" }}>
              工作流预览
            </Title>
          </div>

          <div className="workflow-header-actions">
            <Button
              type="primary"
              // size="large"
              onClick={() => {
                console.log("开始使用工作流", workflowData);
                // 这里可以添加确定使用工作流的逻辑
              }}
              className="workflow-use-button"
            >
              确定使用该工作流
            </Button>
          </div>
        </div>

        <div className="workflow-page-layout">
          {/* 左侧：工作流信息和流程图 */}
          <Card className="workflow-left-panel">
            <div className="workflow-info">
              <Title heading={3} style={{ color: "#1a202c" }}>
                {workflowData?.name}
              </Title>
            </div>

            <Tabs type="line">
              <TabPane
                tab={
                  <span>
                    <IconCode style={{ marginRight: "8px" }} />
                    工作流步骤
                  </span>
                }
                itemKey="steps"
              >
                <div className="workflow-steps">
                  {isWorkflowLoading ? (
                    <div className="workflow-loading-container" style={{
                      display: 'flex',
                      flexDirection: 'column',
                      alignItems: 'center',
                      justifyContent: 'center',
                      padding: '60px 20px',
                      textAlign: 'center'
                    }}>
                      <Spin size="large" />
                      <Text style={{ marginTop: '16px', color: '#666' }}>
                        {isAiTyping ? '正在等待AI回复...' : '正在更新工作流...'}
                      </Text>
                      <Text style={{ marginTop: '8px', fontSize: '12px', color: '#999' }}>
                        {isAiTyping ? '根据您的输入生成回复' : '工作流即将根据对话内容进行调整'}
                      </Text>
                    </div>
                  ) : (
                    <div className="workflow-steps-container">
                      {workflowData?.steps?.map((step, index) => (
                      <div key={step.id} className="workflow-step-item">
                        <div className={`workflow-step-number ${step.type}`}>
                          {step.stepNumber}
                        </div>
                        <div className="workflow-step-content">
                          <Title
                            heading={5}
                            style={{ margin: "0 0 4px 0", color: "#1a202c" }}
                          >
                            {step.name}
                          </Title>
                          <Text
                            type="secondary"
                            style={{ fontSize: "13px", marginBottom: "8px" }}
                          >
                            {step.description}
                          </Text>

                          {/* 显示节点类型和可能的分支 */}
                          <div className="workflow-step-details">
                            <div
                              className={`workflow-step-type-badge ${step.type}`}
                            >
                              {step.typeText}
                            </div>

                            {/* 显示是否为主路径 */}
                            {step.isMainPath === false && (
                              <div className="workflow-branch-badge">分支</div>
                            )}

                            {/* 如果是条件分支，显示分支信息 */}
                            {step.nodeType === "CONDITION_BRANCH" &&
                              step.edges.length > 1 && (
                                <div
                                  style={{ fontSize: "11px", color: "#666" }}
                                >
                                  分支:{" "}
                                  {step.edges
                                    .map((edge) => edge.sourceHandle)
                                    .join(" / ")}
                                </div>
                              )}

                            {/* 如果有循环，显示循环标识 */}
                            {step.edges.some((edge) =>
                              workflowData.steps.some(
                                (s) =>
                                  s.id === edge.targetNodeId &&
                                  s.stepNumber <= step.stepNumber,
                              ),
                            ) && (
                              <div className="workflow-loop-badge">循环</div>
                            )}
                          </div>

                          {/* 显示连接的下一步节点 */}
                          {step.edges.length > 0 && (
                            <div className="workflow-next-step-info">
                              下一步:{" "}
                              {step.edges
                                .map((edge) => {
                                  const nextStep = workflowData.steps.find(
                                    (s) => s.id === edge.targetNodeId,
                                  );
                                  return nextStep
                                    ? `${nextStep.name}(${edge.sourceHandle})`
                                    : edge.targetNodeId;
                                })
                                .join(", ")}
                            </div>
                          )}
                        </div>
                      </div>
                    ))}
                    </div>
                  )}
                </div>
              </TabPane>

              <TabPane
                tab={
                  <span>
                    <IconBranch style={{ marginRight: "8px" }} />
                    流程图
                  </span>
                }
                itemKey="diagram"
              >
                <div className="workflow-mermaid-container">
                  {mermaidCode ? (
                    <DynamicFlowchart code={mermaidCode} />
                  ) : (
                    <div
                      style={{
                        textAlign: "center",
                        padding: "40px",
                        color: "#666",
                      }}
                    >
                      <Text>流程图正在生成中...</Text>
                    </div>
                  )}
                </div>
              </TabPane>
            </Tabs>
          </Card>

          {/* 右侧：AI助手聊天界面 */}
          <div className="workflow-right-panel">
            <div className="workflow-chat-header">
              <Title heading={4} style={{ margin: 0, color: "#1a202c" }}>
                AI工作流助手
              </Title>
            </div>

            <Chat
              chats={messages}
              onChatsChange={handleChatsChange}
              onMessageSend={handleMessageSend}
              showStopGenerate={isAiTyping}
              onStopGenerator={() => {
                // 取消SSE请求
                if (currentSSEController.current) {
                  currentSSEController.current.abort();
                  currentSSEController.current = null;
                }
                setIsAiTyping(false);
                console.log("停止生成");
              }}
              roleConfig={{
                user: {
                  name: "用户",
                  avatar:
                    "https://lf3-static.bytednsdoc.com/obj/eden-cn/ptlz_zlp/ljhwZthlaukjlkulzlp/root-web-sites/avatarDemo.jpeg",
                },
                assistant: {
                  name: "Agentify AI",
                  avatar: "/logo.png",
                },
              }}
              placeholder="输入您的问题或修改建议..."
              mode="bubble"
              align="leftRight"
              enableUpload={false}
            />
          </div>
        </div>
      </div>
    </Content>
  );
}

export default Workflow;
