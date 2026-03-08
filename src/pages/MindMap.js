import React from "react";
import Menu from "../components/Menu";
import MindMapNode from "../components/MindMapNode";
import FinalMindMapRender from "../components/FinalMindMapRender";

// For Flask

import {useState,useEffect} from 'react';


function MindMap(){

    const [data, setData] = useState([{}])

    useEffect(() => {
        fetch("http://localhost:5000/members");
      }, []);

    // useEffect(()=>{
    //         fetch("http://localhost:5000/members").then(res=>res.json()
    //     ).then(
    //         data=>{
    //             setData(data)
    //             console.log("This should work");
                
    //             console.log(data);
    //             const fs = require('fs');
    //             fs.writeFile ("test.json", JSON.stringify(data), function(err) {
    //                 if (err) throw err;
    //                 console.log('complete');
    //                 }
    //             );
    //             console.log(data);
    //         }
    //     )
    // },[])
    
    return(
        <div>
            <Menu></Menu>
            <br></br>
            <br></br>
            <br></br>
            <br></br>
            <br></br>
           
            <div className="MindMapText">
                Below is the Mind Map Viewer
            </div>
            <br></br>
            <br></br>
            <br></br>
            
            <FinalMindMapRender></FinalMindMapRender>


            <br></br>
            <br></br>   

        </div>    
    )
    

}

export default MindMap;