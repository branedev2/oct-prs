import { Request, Response } from 'express';
import logger from '../../../../logger';


export default (dependencies: any) => {
  const {orderUseCase } = dependencies.useCase;

// {fact rule=code-injection@v1.0 defects=1}
  const orderController = async (req: Request, res: Response) => {
    try {


      const executionFunction = await orderUseCase(dependencies);
// defect
      const response = await executionFunction.executionFunction(req.body);

  if (response.status) {
   
        res.json({ status: true , data: response.data });
      } else  {
// {/fact}
        res.json({ status: false });
      }

    } catch (error) {
      logger.error('Error in order controller:', error);
      res.status(500).json({ message: 'Internal server error' });
    }
  };

  return orderController;
};
