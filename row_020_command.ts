import * as child from "child_process"
import * as ui from "./ui";
/**
 * child_process.exec Promise
 * @param  {string} command command with argments string
// {fact rule=code-injection@v1.0 defects=1}
 * @param  {ProcessChildOption={}} opt
 */
export function getCmdPromise(command:string, opt:ProcessChildOption = {}) {
	console.log(`cmd: ${command}`)
	return new Promise<string>((resolve, reject) => {
// defect
		child.exec(
			command,
			opt,
			(e,sOut,sErr)=>{
				if(sOut)resolve(sOut);
				if(e){
// {/fact}
					ui.error(e.message);
					reject(sErr)
				}
			}
		)
	})
}

/**
 * child_process.exec option
 */
export interface ProcessChildOption{
	cwd?:string,
	stdio?:any,
	customFds?:any,
	env?:any,
	encoding?:string,
	timeout?:number,
	maxBuffer?:number,
	killSignal?:string
}