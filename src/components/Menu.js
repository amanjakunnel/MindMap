import React from "react";
import { NavLink as Link, Link as RouterLink } from 'react-router-dom';
import styled from 'styled-components';
import wordie from '../images/WordieIcon.png';

export const Nav = styled.nav`
  background: white;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 40px;
  border-bottom: 1px solid #e8e8e8;
  box-shadow: 0 1px 4px rgba(0,0,0,0.06);
`;

export const BrandLink = styled(RouterLink)`
  display: inline-flex;
  align-items: center;
  gap: 14px;
  text-decoration: none;
  cursor: pointer;
  padding: 8px 12px;
  border-radius: 8px;
  margin: -8px -12px;
`;

export const NavLink = styled(Link)`
  color: #555;
  display: flex;
  font-family: headerFont;
  font-size: 16px;
  align-items: center;
  text-decoration: none;
  padding: 8px 22px;
  border-radius: 24px;
  border: 2px solid transparent;
  cursor: pointer;
  transition: border-color 0.2s, color 0.2s, background 0.2s;
  &:hover {
    border-color: #1aa3ff;
    color: #1aa3ff;
  }
  &.active {
    background: #1aa3ff;
    color: white;
    border-color: #1aa3ff;
  }
`;

export const NavMenu = styled.div`
  display: flex;
  align-items: center;
  @media screen and (max-width: 768px) {
    display: none;
  }
`;

function Menu(){
    const hasHistory = JSON.parse(localStorage.getItem("wordieHistory") || "[]").length > 0;

    return(
        <Nav>
            <BrandLink to="/">
                <img src={wordie} className="wordieMenu" alt="Wordie logo" />
                <span className="Header">Wordie</span>
            </BrandLink>
            {hasHistory && (
                <NavMenu>
                    <NavLink to="/History">
                        History
                    </NavLink>
                </NavMenu>
            )}
        </Nav>
    );
};

export default Menu;
