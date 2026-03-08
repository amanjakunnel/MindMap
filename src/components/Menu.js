import React from "react";
import { NavLink as Link } from 'react-router-dom';
import styled from 'styled-components';
import wordie from '../images/WordieIcon.png';


// import { NavigationContainer } from '@react-navigation/native';
// import { createNativeStackNavigator } from '@react-navigation/native-stack';


export const Nav = styled.nav`
  background: white;
  height: 80px;
  display: flex;
  justify-content: space-around ;
  // justify-content: space-between ;
  padding: 5px;
`;

export const NavLink = styled(Link)`
  color:black;
  display: flex;
  font-size:22px;
  font-weight: 600;
  align-items: center;
  text-decoration: none;
  padding: 0 1.3rem;
  cursor: pointer;
  &.active {
    color: #1aa3ff;
  }
`;


export const NavMenu = styled.div`
  padding-top:110px;
  display: flex;
  align-items: center;
  // margin-right: -24px;
  @media screen and (max-width: 768px) {
    display: none;
  }
`;

function Menu(){
    return(
        <div>
          
            <div className="Container">

                <Nav>
                    <a href="http://localhost:3000">
                    <img src={wordie} className="wordieMenu"></img>
                    </a>
                    {/* <Link to={"/"}>  */}
                      {/* <img src={wordie} className="wordieMenu"></img> */}
                    {/* </Link>  */}

                   {/* <NavLink to={"/"}> */}
                   <a href="http://localhost:3000" className="impLink">
                    
                    <div class="MenuFlex">
                      
                      <br></br>
                      <div className="Header">
                        Wordie
                      </div>
                    </div>
            
                  {/* </NavLink> */}
                  </a>

                    <NavMenu>
                      <NavLink to="/MindMap" activestyle className="Navlinks">
                        Mind Map
                      </NavLink >

                    </NavMenu>
              
              </Nav> 

      </div>
        </div>
    );
};

export default Menu;