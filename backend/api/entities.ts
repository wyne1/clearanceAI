import type { Hono } from 'hono';

type Bindings = { 
  DB: D1Database; 
  ASSETS: Fetcher;
  PYTHON_SERVICE_URL?: string;
};
type App = Hono<{ Bindings: Bindings }>;

export default (app: App) => {
  app.post('/api/entities/research', async (c) => {
    try {
      const pythonServiceUrl = c.env.PYTHON_SERVICE_URL || 'http://localhost:8000';
      const entityRequest = await c.req.json();

      // Proxy request to Python service
      const response = await fetch(`${pythonServiceUrl}/api/entities/research`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(entityRequest),
      });

      if (!response.ok) {
        const errorText = await response.text();
        return c.json(
          { error: 'Entity research failed', details: errorText },
          response.status
        );
      }

      const research = await response.json();
      return c.json(research);
    } catch (error) {
      console.error('Entity research proxy error:', error);
      return c.json(
        { error: 'Failed to connect to AI service', details: error instanceof Error ? error.message : 'Unknown error' },
        500
      );
    }
  });
};

