import React from "react";
import Menu from "../components/Menu";
import Bounce from 'react-reveal/Bounce';
import Jump from 'react-reveal/Jump';
import FileUploader from "../components/FileUploader";

function Home(){
    return(
        <div>
            <Menu></Menu>
            <br></br>
            <br></br>
            <br></br>
            <br></br>
            <br></br>
            <Bounce left    >
                <div className="HomeText">  
                    Hey there !!
                    <br></br>
                    I'm Wordie. Upload a word, pdf or text file, so that I 
                    <br></br>
                    can help you make a Mind Map 
                    <Jump> :) </Jump>
                </div>
            </Bounce>
            <br></br>
            <br></br>
            <br></br>
            <div className="HomeText">  
                    Please upload your text file below:
            </div>
            <br></br>
            <br></br>

            <center>
            <FileUploader></FileUploader>
            </center>
        </div>
    );
};

export default Home;