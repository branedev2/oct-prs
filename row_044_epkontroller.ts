import { Controller, Post, Get, Body, Req, Res, UseGuards, Query, Param, Delete } from '@nestjs/common';
import { Request, Response } from 'express';
import { AuthGuard } from 'src/Guards/auth.guard';
import { ResponseHandler } from 'src/utils/response.handler';
import { CreateEpkDto } from './dtos/create-epk.dto';
import { EpkService } from './epk.service';
import { Model, Types } from 'mongoose';
import { InviteMembersDto } from './dtos/invite-members.dto';
import { DeleteDto } from './dtos/delete.dto';
import * as ejs from 'ejs';
// import * as jsreport from 'jsreport';
// let jsReportInitialized = false;
import * as fs from 'fs';
import * as path from 'path';
import * as moment from 'moment';
import { ConfigService } from '@nestjs/config';
import { S3FileUpload } from 'src/utils/s3';
import { Mailer } from 'src/utils/mailService';
import { EpkPagesService } from './epk-pages/epk-pages.service';

let gIntDataPerPage = 10;

@Controller('epk')
export class EpkController {
    constructor(
        private response: ResponseHandler,
        private epk: EpkService,
        private config: ConfigService,
        private s3: S3FileUpload,
        private mailer: Mailer,
        private pages: EpkPagesService
    ) { };

    @Post('/create')
    @UseGuards(AuthGuard)
    async createEpk(@Req() req: Request, @Res() res: Response, @Body() body: CreateEpkDto) {
        try {
            const { epkId, epkName, width, height,  projectId } = body;

            if(epkId && epkId.toString().length == 24) {
                let ifepKExsist = await this.epk.findOneEpk({ _id: Types.ObjectId(epkId.toString()), userId: req.user._id, status: 1 })

                if (ifepKExsist == null) {
                    return this.response.error(res, 400, "EpK does not exsist")
                };

                Object.assign(ifepKExsist, { epkName });
                await ifepKExsist.save();
                return this.response.success(res, ifepKExsist, "Epk updated successfully")
            } else {
                let ifepKExsist = await this.epk.findOneEpk({ epkName, userId: req.user._id, status: 1, projectId })

                if (ifepKExsist !== null) {
                    return this.response.error(res, 400, "EpK already exsist under the same name")
                };
                
                this.epk.createEpk({
                    epkName,
                    projectId: Types.ObjectId(projectId.toString()),
                    userId: req.user._id,
                    width,
                    height
                }).then(data => {
                    return this.response.success(res, data, "Epk created successfully")
                }).catch(err => {
                    return this.response.error(res, 400, err)
                });  
            }
        } catch (e) {
            return this.response.errorInternal(e, res)
        }
    };

    @Get()
    @UseGuards(AuthGuard)
    async getAllEpk(@Req() req: Request, @Res() res: Response) {
        try {
            gIntDataPerPage = req.query.offset ? Number(req.query.offset) : 15

            //Pagination
            let page = Number(req.query.page) || 1;
            let skipRec = page - 1;
            skipRec = skipRec * gIntDataPerPage;

            let limit = Number(req.query.limit);
            let pageLimit;

            if (limit) {
                pageLimit = limit;
            } else {
                pageLimit = gIntDataPerPage;
            };

            let searchObj = {
                status: 1,
                $and: [
                    {
                        $or: [
                            { "userId._id": req.user._id },
                            { "invitemembers.email": { $in: [req.user.email] } },
                            { "projectTeamMembers.projectTeamMember.email": req.user.email }, 
                            { "projectTeamMembers.createdBy": req.user._id }, 
                        ]
                    }
                ]
            };

            let sortObj = {};
            sortObj = { 'createdAt': -1 };

            if (req.query.q !== undefined) {
                searchObj["$or"] = [
                    { "epkName": { $regex: req.query.q, "$options": "i" } },
                ]
            };

            if (req.query.sort !== undefined && req.query.sort.length > 0 && req.query.type !== undefined && req.query.type.length > 0) {
                if (req.query.type == 'asc') {
                    switch (req.query.sort) {
                        case 'epkName':
                            sortObj = { 'epkName': 1 };
                            break;
                    }
                } else {
                    switch (req.query.sort) {
                        case 'epkName':
                            sortObj = { 'epkName': -1 };
                            break;
                    }
                }
            };

            let countObj = {
                status: 1,
                $and: [
                    {
                        $or: [
                            { "userId": req.user._id },
                            { "invitemembers.email": { $in: [req.user.email] } },
                            { "projectTeamMembers.projectTeamMember.email": req.user.email }, 
                            { "projectTeamMembers.createdBy": req.user._id }, 
                        ]
                    }
                ]
            };

            if (req.query.projectId !== undefined) {
                searchObj["projectId"] = Types.ObjectId(req.query.projectId.toString());
                countObj["projectId"] = Types.ObjectId(req.query.projectId.toString());
            };

            if (req.params.projectId !== undefined) {
                searchObj["projectId"] = Types.ObjectId(req.params.projectId.toString());
                countObj["projectId"] = Types.ObjectId(req.params.projectId.toString());
            };

            let count = await this.epk.getTotalCount(countObj)

            this.epk.getAllEpkMembers(searchObj, skipRec, pageLimit, sortObj).then(async data => {
                for(let x of data) {
                    if(x.epktemplates.length > 0) {
                        x["url"] = await this.s3.s3GetSignedURL(x.epktemplates[0]["preview"])
                    }
                }

                let lObjEpkData = {
                    epks: data,
                    total: Math.round(count.length / (limit ? limit : gIntDataPerPage)),
                    per_page: limit ? limit : gIntDataPerPage,
                    currentPage: page,
                    count: count.length
                }

                return this.response.success(res, lObjEpkData, "Epks fetched successfully")
            }).catch(err => {
                return this.response.error(res, 400, err)
            });

        } catch (e) {
            return this.response.errorInternal(e, res)
        }
    };

    @Get("/single/:epkId")
    @UseGuards(AuthGuard)
    async getEpkById(@Req() req: Request, @Res() res: Response, @Param('epkId') epkId: string) {
        try {

            let checkAccess = await this.epk.checkAccess({
                status: 1,
                _id: Types.ObjectId(epkId),
                $or: [
                    { userId: req.user._id },
                    { "invitemembers.email": { $in: [req.user.email] } },
                    { "projectTeamMembers.projectTeamMember.email": req.user.email }, 
                    { "projectTeamMembers.createdBy": req.user._id }, 
                    {"individualInvites.inviteInfo.email": req.user.email },
                    {"individualInvites.createdBy": req.user._id }
                ]
            });

            if(checkAccess == null || checkAccess == undefined || Object.keys(checkAccess).length == 0) {
                return this.response.noAccess(res, 'You dont have the access to view this epk')
            };

            const findEpk = await this.epk.getEpkData(epkId)
        
            if (findEpk) {
                return this.response.success(res, findEpk, "Epk Fetched successfully");
            } else {
                return this.response.error(res, 400, "Epk not found");
            }

        } catch (e) {
            return this.response.errorInternal(e, res)
        }
    };

    @Post("/create-team")
    @UseGuards(AuthGuard)
    async inviteMembers(@Req() req: Request, @Res() res: Response, @Body() body: InviteMembersDto) {
        try {
            const { epkId, addMembers, removeMembers } = body;

            let ifContractExsist = await this.epk.findOneEpk({ _id: Types.ObjectId(epkId), userId: req.user._id });

            if (ifContractExsist == null) {
                return this.response.error(res, 400, 'Epk dont exsist please check')
            };

            if (addMembers.length > 0) {
                for (let member of addMembers) {
                    if (member.email == req.user.email) {
                        return this.response.error(res, 400, 'You cant add yourself as epk')
                    };

                    let checkMemberAlreadyExsist = await this.epk.checkSigners({
                        epkId,
                        email: member.email,
                        createdBy: req.user._id,
                        status: 1
                    });

                    if (checkMemberAlreadyExsist) {
                        return this.response.error(res, 400, `${member.name} already added to the epk`)
                    };

                    await this.epk.createMembers({
                        epkId,
                        name: member.name || '',
                        email: member.email,
                        createdBy: Types.ObjectId(req.user._id)
                    });

                    const mailOptions = {
                        from: process.env.ADMIN_EMAIL,
                        to: member.email, // list of receivers
                        subject: `Cineacloud | EPK Invite`, // Subject line
                        template: 'individual_invite',
                        'h:X-Mailgun-Variables': JSON.stringify({
                            "userName": `${member.name}`,
                            "app": "props",
                            "appName": `${ifContractExsist.epkName}`,
                            "inviter_name": req.user.firstName,
                            "verifyLink": `${process.env.NODE_URL_1}/users/loginnew`,
                            "function": "invited to"
                        })
                    };
    
                    await this.mailer.send(mailOptions)
                }

                let epk = await this.epk.getAllMembersByEpk(epkId)

                return this.response.success(res, epk, 'Signers added successfully')
            }

            if (removeMembers.length > 0) {
                for (let member of removeMembers) {
                    let checkSigners = await this.epk.checkSigners({
                        epkId,
                        email: member.email,
                        createdBy: req.user._id,
                        status: 1
                    });

                    if (checkSigners) {
                        await this.epk.deleteMembers({
                            epkId,
                            email: member.email,
                            createdBy: req.user._id,
                            status: 1
                        });

                        const mailOptions = {
                            from: process.env.ADMIN_EMAIL,
                            to: member.email, // list of receivers
                            subject: `Cineacloud | EPK Invite`, // Subject line
                            template: 'individual_invite',
                            'h:X-Mailgun-Variables': JSON.stringify({
                                "userName": `${member.name}`,
                                "app": "props",
                                "appName": `${ifContractExsist.epkName}`,
                                "inviter_name": req.user.firstName,
                                "verifyLink": `${process.env.NODE_URL_1}/users/loginnew`,
                                "function": "removed from"
                            })
                        };
        
                        await this.mailer.send(mailOptions)
                    }
                }

                let epk = await this.epk.getAllMembersByEpk(epkId)

                return this.response.success(res, epk, 'Member removed successfully')
            }
        } catch (e) {
            return this.response.errorInternal(e, res)
        }
    }

    @Get("/list-members/:epkId")
    @UseGuards(AuthGuard)
    async listMembers(@Req() req: Request, @Res() res: Response, @Param('epkId') epkId: string) {
        try {
            this.epk.getAllMembersByEpk(epkId).then(data => {
                return this.response.success(res, data, "Members Fetched successfully")
            }).catch(err => {
                return this.response.error(res, 400, err)
            });

        } catch (e) {
            return this.response.errorInternal(e, res)
        }
    };

    @Post('/delete')
    @UseGuards(AuthGuard)
    async deleteEpkId(@Req() req: Request, @Res() res: Response, @Body() body: DeleteDto) {
        try {
            let ifUhaveAccess = await this.epk.findOneEpk({
                _id: body.epkId,
                status: 1,
                userId: req.user._id
            });
            
            if(ifUhaveAccess == null) {
                return this.response.noAccess(res, "You don't have acces to delete the epk, please try again")
            }

            this.epk.deleteEpk({
                _id: body.epkId,
                status: 1,
                userId: req.user._id
            }).then(data => {
                return this.response.success(res, '', "Epk deleted successfully")
            }).catch(err => {
                return this.response.error(res, 400, err)
            });
        } catch (e) {
            return this.response.errorInternal(e, res);
        }
    };

    @Post('/remove-many')
    @UseGuards(AuthGuard)
    async deleteManyEpk(@Req() req: Request, @Res() res: Response, @Body() body: any) {
        try {
            const { deleteIds } = body;

            let searchObj = {
                _id: { $in: deleteIds },
                userId: req.user._id,
                status: 1
            };
            

            this.epk.deleteManyEpk(searchObj).then(data => {
                return this.response.success(res, '', "Epk deleted successfully")
            }).catch(err => {
                return this.response.error(res, 400, err)
            });
        } catch (e) {
            return this.response.errorInternal(e, res);
        }
    };

    /**
     * Export PDF
     * @param req epkId 
     * @param res filepath string
     * @param epkId 
     * @returns string
     */

    @Get('/download')
    @UseGuards(AuthGuard)
    async downloadEpk(@Req() req: Request, @Res() res: Response, @Query('epkId') epkId: string) {
        try {
            if (req.query.epkId == undefined) {
                return this.response.error(res, 400, 'Please provide the epkId')
            };

            let ifEpkExsist = await this.epk.findOneEpk({
                _id: epkId,
                status: 1
            });

            if (ifEpkExsist == null) {
                return this.response.error(res, 400, "Epk does not exsist");
            };

            let templates = await this.pages.getPagesForExportByEpkId({
                epkId: Types.ObjectId(epkId),
                status: 1
            });

            if (templates.length < 0) {
                return this.response.error(res, 400, "Epk Template does not exsist");
            }

            for (let template of templates) {
                template["url"] = template?.previewImg;
// {fact rule=code-injection@v1.0 defects=1}
            }

            let date = moment().utcOffset("+05:30").format('DD/MM/YYYY, hh:mm A');

            var content = fs.readFileSync(path.join(__dirname, '../../public/templates/epk.ejs'), 'utf8');
// defect
            const html = ejs.render(content, {
                templates,
                ifEpkExsist,
                firstName: req.user.firstName,
                lastName: req.user.lastName,
                base_url: this.config.get('BASE_URL'),
// {/fact}
                count: templates.length,
                date: date
            });

            // if (!jsReportInitialized) {
            //     await jsreport().init();
            //     jsReportInitialized = true;
            // }

            // jsreport.render({
            //     template: {
            //         content: html,
            //         engine: 'handlebars',
            //         recipe: 'chrome-pdf'
            //     }
            // }).then((out) => {
            //     let epkName = `epk-${Date.now()}.pdf`;
            //     let pdfPath = path.join(__dirname, `../../public/${epkName}`)
            //     var output = fs.createWriteStream(pdfPath)
            //     out.stream.pipe(output);
            //     out.stream.on('end', () => {
            //         let filepathfromResponse = pdfPath
            //         let lastParam = filepathfromResponse.split('/')
            //         let length = lastParam.length
            //         let filepath = { path: `${this.config.get('BASE_URL')}templates/${epkName}` };
                    return this.response.success(res, 'filepath', 'All Template exported successfully')
            //     })
            // }).catch((e) => {
            //     return this.response.forbiddenError(res, 'Something went wrong. Please try again.')
            // });
        } catch (error) {
            console.log(error)
            return this.response.errorInternal(error, res)
        }
    }

    @Post('/remove-pdf')
    @UseGuards(AuthGuard)
    async removePDF(@Req() req: Request, @Res() res: Response, @Body() body: { url: string }) {
        try {
            let lastParam = body.url.split('/');
            let length = lastParam.length;

            if (fs.existsSync(path.join(__dirname, `../../public/${lastParam[length - 1]}`))) {
                fs.unlinkSync(path.join(__dirname, `../../public/${lastParam[length - 1]}`))
            }

            return this.response.success(res, '', "Remove successfully")
        } catch (e) {
            return this.response.errorInternal(e, res);
        }
    }
}   
