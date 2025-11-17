import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { StatCard } from '@/components/StatCard';
import { RiskBadge } from '@/components/RiskBadge';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { Activity, AlertTriangle, Clock, TrendingUp, Shield } from 'lucide-react';
import { dashboardStats, mockShipments } from '@/lib/mockData';
import { Button } from '@/components/ui/button';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';

export default function Dashboard() {
  const recentAlerts = mockShipments.filter(s => s.riskLevel === 'high' || s.riskLevel === 'medium').slice(0, 5);

  return (
    <div className="container mx-auto px-4 py-8" data-page="dashboard">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold tracking-tight mb-2">Risk Assessment Dashboard</h1>
          <p className="text-muted-foreground">
            AI-powered compliance monitoring for Mexican customs brokers
          </p>
        </div>

        {/* Stats Grid */}
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4 mb-8">
          <StatCard
            title="Total Assessments"
            value={dashboardStats.totalAssessments}
            icon={Activity}
            description="This month"
            trend={{ value: 12, isPositive: true }}
          />
          <StatCard
            title="High Risk Alerts"
            value={dashboardStats.highRiskAlerts}
            icon={AlertTriangle}
            description="Requiring immediate attention"
          />
          <StatCard
            title="Pending Review"
            value={dashboardStats.pendingReview}
            icon={Clock}
            description="Awaiting broker decision"
          />
          <StatCard
            title="Avg Processing Time"
            value={dashboardStats.avgProcessingTime}
            icon={TrendingUp}
            description="85% faster than manual"
          />
        </div>

        {/* Charts Row */}
        <div className="grid gap-4 md:grid-cols-2 mb-8">
          {/* Risk Distribution */}
          <Card data-chart="risk-distribution">
            <CardHeader>
              <CardTitle>Risk Distribution</CardTitle>
              <CardDescription>Current month assessment breakdown</CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={dashboardStats.riskDistribution}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, value }) => `${name}: ${value}`}
                    outerRadius={100}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {dashboardStats.riskDistribution.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          {/* Weekly Trend */}
          <Card data-chart="weekly-trend">
            <CardHeader>
              <CardTitle>Weekly Activity</CardTitle>
              <CardDescription>Assessments and alerts over the past week</CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={dashboardStats.weeklyTrend}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="day" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="assessments" fill="#3b82f6" name="Assessments" />
                  <Bar dataKey="alerts" fill="#ef4444" name="Alerts" />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </div>

        {/* Recent Alerts */}
        <Card className="mb-8" data-section="recent-alerts">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>Recent Risk Alerts</CardTitle>
                <CardDescription>Shipments requiring attention</CardDescription>
              </div>
              <Button asChild variant="outline" size="sm">
                <Link to="/history">View All</Link>
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Shipment ID</TableHead>
                  <TableHead>Date</TableHead>
                  <TableHead>Shipper</TableHead>
                  <TableHead>Commodity</TableHead>
                  <TableHead>Risk Level</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Action</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {recentAlerts.map((shipment) => (
                  <TableRow key={shipment.id}>
                    <TableCell className="font-mono text-sm">{shipment.id}</TableCell>
                    <TableCell>{new Date(shipment.date).toLocaleDateString()}</TableCell>
                    <TableCell>{shipment.shipper}</TableCell>
                    <TableCell>{shipment.commodity}</TableCell>
                    <TableCell>
                      <RiskBadge level={shipment.riskLevel} score={shipment.riskScore} />
                    </TableCell>
                    <TableCell>
                      <span className="capitalize text-sm text-muted-foreground">
                        {shipment.status.replace('_', ' ')}
                      </span>
                    </TableCell>
                    <TableCell>
                      <Button variant="ghost" size="sm" asChild>
                        <Link to={`/history?id=${shipment.id}`}>Review</Link>
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>

        {/* Top Flags */}
        <Card data-section="top-flags">
          <CardHeader>
            <CardTitle>Most Common Risk Flags</CardTitle>
            <CardDescription>Top issues detected this month</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {dashboardStats.topFlags.map((flag, index) => (
                <div key={index} className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="rounded-full bg-red-100 dark:bg-red-900/20 p-2">
                      <Shield className="h-4 w-4 text-red-600 dark:text-red-400" />
                    </div>
                    <span className="text-sm font-medium">{flag.flag}</span>
                  </div>
                  <span className="text-sm font-bold text-muted-foreground">{flag.count}</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
}
