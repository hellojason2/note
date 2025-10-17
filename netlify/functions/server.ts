import serverless from '@netlify/functions';
import express from 'express';
import { createExpressMiddleware } from '@trpc/server/adapters/express';
import { appRouter } from '../../server/routers';
import { createContext } from '../../server/_core/context';

const app = express();

// tRPC middleware
app.use(
  '/api/trpc',
  createExpressMiddleware({
    router: appRouter,
    createContext,
  })
);

// OAuth routes
import { oauthRouter } from '../../server/_core/oauth';
app.use('/api/oauth', oauthRouter);

export const handler = serverless(app);

