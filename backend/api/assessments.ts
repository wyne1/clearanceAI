import type { Hono } from 'hono';

type Bindings = { 
  DB: D1Database; 
  ASSETS: Fetcher;
  PYTHON_SERVICE_URL?: string;
};
type App = Hono<{ Bindings: Bindings }>;

export default (app: App) => {
  app.post('/api/assess', async (c) => {
    try {
      const pythonServiceUrl = c.env.PYTHON_SERVICE_URL || 'http://localhost:8000';
      const shipmentData = await c.req.json();

      // Proxy request to Python service
      const response = await fetch(`${pythonServiceUrl}/api/assess`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(shipmentData),
      });

      if (!response.ok) {
        const errorText = await response.text();
        return c.json(
          { error: 'Assessment failed', details: errorText },
          response.status
        );
      }

      const assessment = await response.json();
      return c.json(assessment);
    } catch (error) {
      console.error('Assessment proxy error:', error);
      return c.json(
        { error: 'Failed to connect to AI service', details: error instanceof Error ? error.message : 'Unknown error' },
        500
      );
    }
  });
};

