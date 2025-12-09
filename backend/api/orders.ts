import type { Hono } from 'hono';

type Bindings = { 
  DB: D1Database; 
  ASSETS: Fetcher;
  PYTHON_SERVICE_URL?: string;
};
type App = Hono<{ Bindings: Bindings }>;

export default (app: App) => {
  app.post('/api/orders/create', async (c) => {
    try {
      const pythonServiceUrl = c.env.PYTHON_SERVICE_URL || 'http://localhost:8000';
      const orderData = await c.req.json();

      // Proxy request to Python service
      const response = await fetch(`${pythonServiceUrl}/api/orders/create`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(orderData),
      });

      if (!response.ok) {
        const errorText = await response.text();
        return c.json(
          { error: 'Order pre-check failed', details: errorText },
          response.status
        );
      }

      const assessment = await response.json();
      return c.json(assessment);
    } catch (error) {
      console.error('Order pre-check proxy error:', error);
      return c.json(
        { error: 'Failed to connect to AI service', details: error instanceof Error ? error.message : 'Unknown error' },
        500
      );
    }
  });
};

