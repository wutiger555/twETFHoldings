import React from 'react';
import { Nav } from 'react-bootstrap';
import { NavLink } from 'react-router-dom';
import { FiGrid } from 'react-icons/fi'; // Using Feather Icons for a clean look

const Sidebar = () => {
  return (
    <div className="sidebar">
      <h3 className="sidebar-header">ETF 儀表板</h3>
      <Nav className="flex-column sidebar-nav">
        <NavLink to="/" className="nav-link">
          <FiGrid className="sidebar-icon" />
          總覽
        </NavLink>
        {/* Add other navigation links here in the future */}
      </Nav>
    </div>
  );
};

export default Sidebar;