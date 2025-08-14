import { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Layout, Button, Typography, Card, Input, TextArea, Toast, Space } from '@douyinfe/semi-ui';
import { IconArrowLeft, IconSave, IconEdit } from '@douyinfe/semi-icons';
import request from '../utils/request';
import './RequirementForm.css';

const { Content } = Layout;
const { Title, Text } = Typography;

function RequirementForm() {
  const navigate = useNavigate();
  const location = useLocation();
  const threadId = location.state?.threadId || '';
  const requirementData = location.state?.requirementData || null;
  
  const [isEditing, setIsEditing] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [formData, setFormData] = useState({
    requirement_name: requirementData?.requirement_name || '',
    mission_statement: requirementData?.mission_statement || '',
    user_and_scenario: requirementData?.user_and_scenario || '',
    user_input: requirementData?.user_input || '',
    ai_output: requirementData?.ai_output || '',
    success_criteria: requirementData?.success_criteria || '',
    boundaries_and_limitations: requirementData?.boundaries_and_limitations || ''
  });

  if (!requirementData) {
    return (
      <Content className="requirement-form-content">
        <div className="requirement-form-container">
          <Card className="requirement-form-card">
            <div className="error-content">
              <Title heading={2} style={{ textAlign: 'center', color: '#1a202c' }}>
                数据加载失败
              </Title>
              <Text style={{ textAlign: 'center', fontSize: '16px', color: '#666', marginBottom: '24px' }}>
                无法获取需求数据，请返回重试
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

  const handleInputChange = (field, value) => {
    setFormData({
      ...formData,
      [field]: value
    });
  };

  const handleSave = async () => {
    setIsSaving(true);
    
    try {
      const result = await request.post(`/api/requirement/fields/${threadId}`, formData);
      
      if (result.code === 0) {
        setIsEditing(false);
      } else {
        throw new Error(result.message || '保存失败');
      }
    } catch (error) {
      console.error('保存失败:', error);
    } finally {
      setIsSaving(false);
    }
  };

  const handleConfirmRequirement = () => {
    // navigate('/next-page', { state: { threadId, formData } });
  };

  const fieldLabels = {
    requirement_name: '需求名称',
    mission_statement: '使命陈述',
    user_and_scenario: '用户与场景',
    user_input: '用户输入',
    ai_output: 'AI输出',
    success_criteria: '成功标准',
    boundaries_and_limitations: '边界与限制'
  };

  return (
    <Content className="requirement-form-content">
      <div className="requirement-form-container">
        <div className="requirement-form-header">
          <Button 
            icon={<IconArrowLeft />} 
            theme="borderless"
            onClick={() => navigate('/')}
            className="header-button"
          >
            返回首页
          </Button>
          
          <div className="header-info">
            <Title heading={2} style={{ margin: 0, color: '#1a202c' }}>
              需求详情确认
            </Title>
            <Text type="secondary" style={{ marginTop: '8px', display: 'block' }}>
              请确认以下需求信息，您可以进行编辑和修改
            </Text>
          </div>

          <div className="header-actions">
            {!isEditing ? (
              <Button 
                icon={<IconEdit />} 
                theme="borderless"
                onClick={() => setIsEditing(true)}
                className="header-button"
              >
                编辑需求
              </Button>
            ) : (
              <Space>
                <Button 
                  onClick={() => {
                    setIsEditing(false);
                    // 重置为原始数据
                    setFormData({
                      requirement_name: requirementData?.requirement_name || '',
                      mission_statement: requirementData?.mission_statement || '',
                      user_and_scenario: requirementData?.user_and_scenario || '',
                      user_input: requirementData?.user_input || '',
                      ai_output: requirementData?.ai_output || '',
                      success_criteria: requirementData?.success_criteria || '',
                      boundaries_and_limitations: requirementData?.boundaries_and_limitations || ''
                    });
                  }}
                  className="header-button"
                >
                  取消
                </Button>
                <Button 
                  type="primary"
                  icon={<IconSave />}
                  loading={isSaving}
                  onClick={handleSave}
                  className="header-button"
                >
                  {isSaving ? '保存中...' : '保存修改'}
                </Button>
              </Space>
            )}
          </div>
        </div>

        <Card className="requirement-form-card">
          <div className="form-content">
            {Object.entries(fieldLabels).map(([field, label]) => (
              <div key={field} className="form-field">
                <div className="field-label">
                  <Text strong style={{ fontSize: '16px', color: '#1a202c' }}>
                    {label}
                  </Text>
                </div>
                
                <div className="field-content">
                  {isEditing ? (
                    field === 'requirement_name' ? (
                      <Input
                        value={formData[field]}
                        onChange={(value) => handleInputChange(field, value)}
                        placeholder={`请输入${label}`}
                        maxLength={100}
                        showClear
                        className="requirement-name-input"
                      />
                    ) : (
                      <TextArea
                        value={formData[field]}
                        onChange={(value) => handleInputChange(field, value)}
                        placeholder={`请输入${label}`}
                        autosize={{ minRows: 3, maxRows: 8 }}
                        maxLength={2000}
                        showClear
                        className="requirement-textarea"
                      />
                    )
                  ) : (
                    <div className="field-display">
                      <Text style={{ 
                        lineHeight: '1.6', 
                        fontSize: '14px',
                        whiteSpace: 'pre-wrap',
                        color: '#374151'
                      }}>
                        {formData[field] || '暂无内容'}
                      </Text>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>

          {!isEditing && (
            <div className="form-actions">
              <Button 
                type="primary"
                size="large"
                onClick={handleConfirmRequirement}
                className="confirm-button"
              >
                确认需求
              </Button>
            </div>
          )}
        </Card>
      </div>
    </Content>
  );
}

export default RequirementForm;