import React from 'react';
import { Button, Nav } from '@douyinfe/semi-ui';
import {
    IconPlus,
    IconHome,
    IconUser,
    IconSetting,
} from '@douyinfe/semi-icons';
import { useNavigate } from 'react-router-dom';
import './Sidebar.css';

function Sidebar() {
    const navigate = useNavigate();

    const handleNavClick = (data) => {
        navigate(data.itemKey);
    };

    return (
        <div className="floating-sidebar-container">
            
            <div className="plus-button-wrapper">
                <Button
                    icon={<IconPlus size='large'/>}
                    type="primary"
                    theme="outline"
                    style={{ width: 52, height: 52, color: 'white', backgroundColor: '#2d3748', borderRadius: '50%'}}
                />
            </div>

            <div className="nav-pill-wrapper">
                <Nav
                    mode="vertical"
                    defaultSelectedKeys={['/']}
                    onClick={handleNavClick}
                    style={{ 
                        backgroundColor: 'transparent',
                        width: '60px',
                    }}
                    bodyStyle={{ height: 150 }}
                >
                    <Nav.Item 
                        itemKey="/" 
                        icon={<IconHome size='large' style={{ color: '#2d3748' }} />} 
                    />
                    <Nav.Item 
                        itemKey="/community" 
                        icon={<IconUser size='large' style={{ color: '#2d3748' }} />} 
                    />
                    <Nav.Item 
                        itemKey="/settings" 
                        icon={<IconSetting size='large' style={{ color: '#2d3748' }} />} 
                    />
                </Nav>
            </div>
        </div>
    );
}

export default Sidebar;