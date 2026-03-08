import React, {Component,file} from "react";
import axios,{post} from 'axios';


class FileUploader extends Component{

    constructor(props){
        super(props);
        this.state={
            image:''
        }
    }
    onChange(e)
    {
        let files=e.target.files;
        console.log("Data File",files);

        let reader = new FileReader();
        reader.readAsDataURL(files[0]);
        reader.onload=(e)=>{
            // console.warn("File Data",e.target.result)
            const url='';
            const formData={file: e.target.result}
            return post (url,formData).then(response =>console.warn("result",response))
        }
    }
    render(){
        return(

            <div>


                <form action = "http://localhost:5000/saveDoc" method = "post">
                    <input type="file" name="file" onChange={(e)=>this.onChange(e)} className="fileButton" />
                </form>   


                {/* <div onSubmit={this.onFormSubmit}>
                    <input type="file" name="file" onChange={(e)=>this.onChange(e)} className="fileButton" />
                    <div>
				        <button onClick={handleSubmission}>Submit</button>
			        </div>
                </div> */}


            </div>
        );
    }
};

export default FileUploader;