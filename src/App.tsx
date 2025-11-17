import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Dashboard from "./pages/Dashboard";
import NewAssessment from "./pages/NewAssessment";
import EntityIntelligence from "./pages/EntityIntelligence";
import ShipmentHistory from "./pages/ShipmentHistory";
import NotFound from "./pages/NotFound";
import { Navbar } from "@/components/Navbar";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Sonner />
      <BrowserRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
        <div className="min-h-screen bg-background">
          <Navbar />
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/assess" element={<NewAssessment />} />
            <Route path="/entities" element={<EntityIntelligence />} />
            <Route path="/history" element={<ShipmentHistory />} />
            {/* ADD ALL CUSTOM ROUTES ABOVE THE CATCH-ALL "*" ROUTE */}
            <Route path="*" element={<NotFound />} />
          </Routes>
          <footer className="border-t py-6 mt-12">
            <div className="container mx-auto px-4 text-center text-sm text-muted-foreground">
              <p>
                Built with ❤️ by{' '}
                <a
                  href="https://devlo.ai?utm_source=alert-star-9142"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="font-medium hover:text-primary transition-colors"
                >
                  devlo
                </a>
              </p>
            </div>
          </footer>
        </div>
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
