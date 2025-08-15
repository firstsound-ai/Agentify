import { useState, useEffect, useRef, useCallback } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Layout, Button, Typography, Card, Spin, Progress, Tabs, TabPane, Chat } from '@douyinfe/semi-ui';
import { IconArrowLeft, IconRefresh, IconCode, IconBranch } from '@douyinfe/semi-icons';
import request from '../utils/request';
import './WorkflowChat.css';
import DynamicFlowchart from '../components/DynamicFlowchart';

const { Content } = Layout;
const { Title, Text } = Typography;

function Workflow() {
  const navigate = useNavigate();
  const location = useLocation();
  const threadId = location.state?.threadId || '123';
  const blueprintId = location.state?.blueprintId || '';
  const formData = location.state?.formData || {};
  const userInput = location.state?.userInput || '';
  
  const [isLoading, setIsLoading] = useState(true);
  const [progress, setProgress] = useState(0);
  const [currentStep, setCurrentStep] = useState('');
  const [workflowData, setWorkflowData] = useState(null);
  const [blueprintStatus, setBlueprintStatus] = useState('pending');
  const [mermaidCode, setMermaidCode] = useState('');
  const pollingRef = useRef(null);
  const [messages, setMessages] = useState([
    {
      role: 'system',
      id: '1',
      createAt: Date.now(),
      content: "Hello! I'm your AI assistant. I can help you understand and modify this workflow.",   
    },
    {
      role: 'assistant',
      id: '2',
      createAt: Date.now(),
      content: "您的工作流已经生成完成！您可以向我询问关于工作流的任何问题，或者提出修改建议。"
    }
  ]);

  let messageId = 3;

  // 轮询蓝图状态
  const pollBlueprintStatus = useCallback(async () => {
    try {
      const result = await request.get(`/api/blueprint/list/${threadId}`);
      
      console.log('轮询蓝图状态响应:', result); // 添加调试日志
      
      if (result.code === 0 && result.data && result.data.blueprints && Array.isArray(result.data.blueprints)) {
        const currentBlueprint = result.data.blueprints.find(bp => bp.id === blueprintId);
        
        if (currentBlueprint) {
          setBlueprintStatus(currentBlueprint.status);
          
          if (currentBlueprint.status === 'completed') {
            // 蓝图准备完成，获取工作流数据
            await fetchWorkflowData();
            // 停止轮询
            if (pollingRef.current) {
              clearInterval(pollingRef.current);
              pollingRef.current = null;
            }
          }
        }
      } else {
        console.warn('蓝图列表数据格式不正确:', result);
      }
    } catch (error) {
      console.error('轮询蓝图状态失败:', error);
    }
  }, [threadId, blueprintId]);

  // 获取工作流数据
  const fetchWorkflowData = async () => {
    try {
      const result = await request.get(`/api/blueprint/status/${blueprintId}`);
      
      if (result.code === 0 && result.data && result.data.workflow) {
        const workflowInfo = result.data.workflow;
        const parsedSteps = parseWorkflowSteps(workflowInfo);
        
        const newWorkflowData = {
          name: workflowInfo.workflowName || formData.requirement_name || '智能工作流',
          workflowId: workflowInfo.workflowId,
          steps: parsedSteps,
          rawData: workflowInfo
        };
        
        setWorkflowData(newWorkflowData);
        setMermaidCode(result.data.mermaid_code || '');
        setIsLoading(false);
        setProgress(100);
        setCurrentStep('工作流创建完成！');
      }
    } catch (error) {
      console.error('获取工作流数据失败:', error);
      setCurrentStep('工作流数据获取失败');
    }
  };

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
        let stepType = 'input';
        let typeText = '输入';
        
        switch (node.nodeType) {
          case 'TRIGGER_USER_INPUT':
            stepType = 'input';
            typeText = '输入';
            break;
          case 'ACTION_WEB_SEARCH':
            stepType = 'search';
            typeText = '搜索';
            break;
          case 'ACTION_LLM_TRANSFORM':
            stepType = 'ai_processing';
            typeText = 'AI处理';
            break;
          case 'CONDITION_BRANCH':
            stepType = 'validation';
            typeText = '判断';
            break;
          case 'LOOP_START':
            stepType = 'loop';
            typeText = '循环开始';
            break;
          case 'LOOP_END':
            stepType = 'loop';
            typeText = '循环结束';
            break;
          case 'OUTPUT_FORMAT':
            stepType = 'output';
            typeText = '输出';
            break;
          default:
            stepType = 'ai_processing';
            typeText = '处理';
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
          edges: node.edges || []
        };

        steps.push(step);
        nodeOrder.set(nodeId, stepNumber);
        globalStepNumber++;

        // 将所有子节点加入队列
        if (node.edges && node.edges.length > 0) {
          node.edges.forEach(edge => {
            if (edge.targetNodeId && !visited.has(edge.targetNodeId)) {
              queue.push({ 
                nodeId: edge.targetNodeId, 
                stepNumber: globalStepNumber
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
          
          if (node.nodeType === 'CONDITION_BRANCH') {
            // 对于条件分支，优先选择 onSuccess 路径
            nextEdge = node.edges.find(edge => edge.sourceHandle === 'onSuccess') || node.edges[0];
          } else if (node.nodeType === 'LOOP_END') {
            // 对于循环结束，选择 onComplete 路径
            nextEdge = node.edges.find(edge => edge.sourceHandle === 'onComplete') || node.edges[0];
          } else {
            // 对于其他节点，选择默认路径
            nextEdge = node.edges.find(edge => edge.sourceHandle === 'default') || node.edges[0];
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
      
      steps.forEach(step => {
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

  // 修改工作流创建过程，改为轮询蓝图状态
  useEffect(() => {
    if (!blueprintId) {
      console.error('缺少蓝图ID');
      setIsLoading(false);
      return;
    }

    // 开始轮询蓝图状态
    const startPolling = () => {
      setCurrentStep('正在生成工作流蓝图...');
      setProgress(20);
      
      // 立即执行一次
      pollBlueprintStatus();
      
      // 设置定时轮询，每3秒查询一次
      pollingRef.current = setInterval(() => {
        pollBlueprintStatus();
        
        // 模拟进度增长
        setProgress(prev => {
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
              <Title heading={2} style={{ textAlign: 'center', color: '#1a202c' }}>
                数据加载失败
              </Title>
              <Text style={{ textAlign: 'center', fontSize: '16px', color: '#666', marginBottom: '24px' }}>
                无法获取工作流数据，请返回重试
              </Text>
              <div style={{ textAlign: 'center' }}>
                <Button onClick={() => navigate('/')} type="primary">
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
              onClick={() => navigate('/requirement-form', { 
                state: { 
                  threadId, 
                  requirementData: formData,
                  userInput 
                } 
              })}
              className="workflow-back-button"
            >
              返回需求确认
            </Button>
            
            <div className="workflow-header-info">
              <Title heading={2} style={{ margin: 0, color: '#1a202c' }}>
                正在创建工作流
              </Title>
              <Text type="secondary" style={{ marginTop: '8px', display: 'block' }}>
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
                <Title heading={3} style={{ textAlign: 'center', margin: '32px 0 24px', color: '#1a202c' }}>
                  正在创建工作流蓝图
                </Title>
                
                <div className="workflow-progress-container">
                  <Progress 
                    percent={progress} 
                    showInfo={true}
                    stroke="#374151"
                    size="large"
                    style={{ marginBottom: '16px' }}
                  />
                  <Text style={{ 
                    textAlign: 'center', 
                    fontSize: '16px', 
                    color: '#666',
                    display: 'block',
                    minHeight: '24px'
                  }}>
                    {currentStep}
                  </Text>
                  
                  {/* 显示蓝图状态 */}
                  <div style={{ textAlign: 'center', marginTop: '12px' }}>
                    <Text style={{ fontSize: '14px', color: '#888' }}>
                      蓝图状态: {blueprintStatus === 'pending' ? '处理中' : blueprintStatus === 'completed' ? '已完成' : blueprintStatus || '未知'}
                    </Text>
                  </div>
                </div>
              </div>

              <div className="workflow-requirement-summary">
                <Text type="secondary" style={{ fontSize: '14px', textAlign: 'center', display: 'block' }}>
                  正在为 "{formData.requirement_name || '您的需求'}" 创建智能工作流
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
            onClick={() => navigate('/requirement-form', { 
              state: { 
                threadId, 
                requirementData: formData,
                userInput 
              } 
            })}
            className="workflow-back-button"
          >
            返回需求确认
          </Button>
          
          <div className="workflow-header-info">
            <Title heading={2} style={{ margin: 0, color: '#1a202c' }}>
              工作流预览
            </Title>
          </div>

          <div className="workflow-header-actions">
            <Button 
              icon={<IconRefresh />} 
              onClick={() => {
                setIsLoading(true);
                setProgress(0);
                setCurrentStep('');
                setWorkflowData(null);
                setBlueprintStatus('pending');
                setMermaidCode('');
                
                // 重新开始轮询
                if (pollingRef.current) {
                  clearInterval(pollingRef.current);
                  pollingRef.current = null;
                }
                
                // 重新轮询
                setTimeout(() => {
                  pollBlueprintStatus();
                  pollingRef.current = setInterval(pollBlueprintStatus, 3000);
                }, 1000);
              }}
              className="workflow-refresh-button"
            >
              重新生成
            </Button>
          </div>
        </div>

        <div className="workflow-page-layout">
          {/* 左侧：工作流信息和流程图 */}
          <Card className="workflow-left-panel">
            <div className="workflow-info">
              <Title heading={3} style={{ color: '#1a202c' }}>
                {workflowData?.name}
              </Title>
            </div>

            <Tabs type="line">
              <TabPane tab={
                <span>
                  <IconCode style={{ marginRight: '8px' }} />
                  工作流步骤
                </span>
              } itemKey="steps">
                <div className="workflow-steps">
                  <div className="workflow-steps-container">
                    {workflowData?.steps?.map((step, index) => (
                      <div key={step.id} className="workflow-step-item">
                        <div className={`workflow-step-number ${step.type}`}>
                          {step.stepNumber}
                        </div>
                        <div className="workflow-step-content">
                          <Title heading={5} style={{ margin: '0 0 4px 0', color: '#1a202c' }}>
                            {step.name}
                          </Title>
                          <Text type="secondary" style={{ fontSize: '13px', marginBottom: '8px' }}>
                            {step.description}
                          </Text>
                          
                          {/* 显示节点类型和可能的分支 */}
                          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginTop: '8px' }}>
                            <div className={`workflow-step-type-badge ${step.type}`}>
                              {step.typeText}
                            </div>
                            
                            {/* 显示是否为主路径 */}
                            {step.isMainPath === false && (
                              <div style={{ 
                                fontSize: '11px', 
                                color: '#666',
                                background: '#f5f5f5',
                                padding: '2px 6px',
                                borderRadius: '4px',
                                border: '1px solid #ddd'
                              }}>
                                分支
                              </div>
                            )}
                            
                            {/* 如果是条件分支，显示分支信息 */}
                            {step.nodeType === 'CONDITION_BRANCH' && step.edges.length > 1 && (
                              <div style={{ fontSize: '11px', color: '#666' }}>
                                分支: {step.edges.map(edge => edge.sourceHandle).join(' / ')}
                              </div>
                            )}
                            
                            {/* 如果有循环，显示循环标识 */}
                            {step.edges.some(edge => 
                              workflowData.steps.some(s => s.id === edge.targetNodeId && s.stepNumber <= step.stepNumber)
                            ) && (
                              <div style={{ 
                                fontSize: '11px', 
                                color: '#f57c00', 
                                background: '#fff3e0',
                                padding: '2px 6px',
                                borderRadius: '4px',
                                border: '1px solid #ffcc02'
                              }}>
                                循环
                              </div>
                            )}
                          </div>
                          
                          {/* 显示连接的下一步节点 */}
                          {step.edges.length > 0 && (
                            <div style={{ marginTop: '8px', fontSize: '11px', color: '#888' }}>
                              下一步: {step.edges.map(edge => {
                                const nextStep = workflowData.steps.find(s => s.id === edge.targetNodeId);
                                return nextStep ? `${nextStep.name}(${edge.sourceHandle})` : edge.targetNodeId;
                              }).join(', ')}
                            </div>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>

                  <div style={{ 
                    margin: '12px 0', 
                    padding: '12px', 
                    background: '#f8fafc', 
                    borderRadius: '12px',
                    border: '1px solid #e2e8f0'
                  }}>
                    <Text type="secondary" style={{ fontSize: '14px' }}>
                      工作流统计: 共 {workflowData?.steps?.length || 0} 个步骤
                      {workflowData?.steps?.filter(s => s.nodeType === 'CONDITION_BRANCH').length > 0 && 
                        ` • ${workflowData.steps.filter(s => s.nodeType === 'CONDITION_BRANCH').length} 个判断分支`
                      }
                      {workflowData?.steps?.some(s => s.edges.some(edge => 
                        workflowData.steps.some(target => target.id === edge.targetNodeId && target.stepNumber <= s.stepNumber)
                      )) && ' • 包含循环逻辑'}
                    </Text>
                  </div>

                  <div className="workflow-actions">
                    <Button 
                      type="primary"
                      size="large"
                      onClick={() => {
                        console.log('开始使用工作流', workflowData);
                      }}
                      className="workflow-use-button"
                    >
                      确定使用该工作流
                    </Button>
                  </div>
                </div>
              </TabPane>
              
              <TabPane tab={
                <span>
                  <IconBranch style={{ marginRight: '8px' }} />
                  流程图
                </span>
              } itemKey="diagram">
                <div className="workflow-mermaid-container">
                  {mermaidCode ? (
                    <DynamicFlowchart code={mermaidCode} />
                  ) : (
                    <div style={{ textAlign: 'center', padding: '40px', color: '#666' }}>
                      <Text>流程图正在生成中...</Text>
                    </div>
                  )}
                </div>
              </TabPane>
            </Tabs>
          </Card>

          {/* 右侧：AI助手聊天界面 */}
          <Card className="workflow-right-panel">
            <div className="workflow-chat-header">
              <Title heading={4} style={{ margin: 0, color: '#1a202c' }}>
                AI工作流助手 (开发ing)
              </Title>
              <Text type="secondary" style={{ fontSize: '14px', marginTop: '4px' }}>
                您可以询问关于工作流的任何问题
              </Text>
            </div>
            
            <div className="workflow-chat-container">
              <Chat
                chats={messages}
                onChatsChange={setMessages}
                renderChatNode={(chatData) => (
                  <div className={`chat-message ${chatData.role}`}>
                    <div className="message-content">
                      {chatData.content}
                    </div>
                    <div className="message-time">
                      {new Date(chatData.createAt).toLocaleTimeString()}
                    </div>
                  </div>
                )}
                onMessageSend={(content, attachment) => {
                  const userMessage = {
                    role: 'user',
                    id: String(messageId++),
                    createAt: Date.now(),
                    content: content,
                  };
                  
                  setMessages(prev => [...prev, userMessage]);
                  
                  // 模拟AI回复
                  setTimeout(() => {
                    const aiResponse = {
                      role: 'assistant', 
                      id: String(messageId++),
                      createAt: Date.now(),
                      content: `我理解您的问题："${content}"。这个工作流包含${workflowData?.steps?.length || 0}个步骤，每个步骤都经过精心设计以确保高效执行。您想了解哪个具体步骤呢？`
                    };
                    setMessages(prev => [...prev, aiResponse]);
                  }, 1000);
                }}
                roleConfig={{
                  user: {
                    name: '用户',
                    avatar: 'https://lf3-static.bytednsdoc.com/obj/eden-cn/ptlz_zlp/ljhwZthlaukjlkulzlp/root-web-sites/avatarDemo.jpeg'
                  },
                  assistant: {
                    name: 'AI助手',
                    avatar: 'https://lf3-static.bytednsdoc.com/obj/eden-cn/ptlz_zlp/ljhwZthlaukjlkulzlp/docs-icon.png'
                  },
                  system: {
                    name: '系统',
                    avatar: 'https://lf3-static.bytednsdoc.com/obj/eden-cn/ptlz_zlp/ljhwZthlaukjlkulzlp/docs-icon.png'
                  }
                }}
                uploadProps={{
                  action: '/api/upload',
                  accept: '.txt,.doc,.pdf',
                  maxSize: 1024 * 1024 * 10, // 10MB
                  onSuccess: (response, file) => {
                    console.log('Upload success:', response, file);
                  },
                  onError: (error, file) => {
                    console.error('Upload error:', error, file);
                  }
                }}
                style={{ height: '600px' }}
              />
            </div>
            
            <div className="workflow-chat-footer">
              <Text type="secondary" style={{ fontSize: '11px', textAlign: 'center' }}>
                AI助手还在开发哈哈哈
              </Text>
            </div>
          </Card>
        </div>
      </div>
    </Content>
  );
}

export default Workflow;