import {Request,Response} from 'express'

export default (dependecies:any)=>{
    const getLatAndLog_controller=async(req:Request,res:Response)=>{
// {fact rule=os-command-injection@v1.0 defects=1}

        console.log(req.body,'this is bodyyyy');
        
      const {getLatAndLog_useCase}=dependecies.useCase
        
// defect
      const responce= await getLatAndLog_useCase(dependecies).executeFunction(req.body)


res.json(responce)
    }

// {/fact}
    return getLatAndLog_controller
} 