import React from "react";
import Menu from "../components/Menu";
import FileUploader from "../components/FileUploader";

function Home(){
    return(
        <div>
            <Menu></Menu>
            <div className="HomeContainer homeAnimate">
                <div className="HomeText">
                    Turn documents into Mind Maps.
                </div>
                <div className="HomeSubText">
                    Upload a .docx, .pdf, or .txt file and Wordie will map it out for you.
                </div>
                <div className="UploadSection">
                    <FileUploader />
                </div>
            </div>
        </div>
    );
};

export default Home;