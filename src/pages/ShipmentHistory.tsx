import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Button } from '@/components/ui/button';
import { RiskBadge } from '@/components/RiskBadge';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Search, Filter, Download, Eye } from 'lucide-react';
import { mockShipments } from '@/lib/mockData';
import type { ShipmentRecord } from '@/lib/mockData';
import { motion } from 'framer-motion';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';

export default function ShipmentHistory() {
  const [searchTerm, setSearchTerm] = useState('');
  const [riskFilter, setRiskFilter] = useState<string>('all');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [selectedShipment, setSelectedShipment] = useState<ShipmentRecord | null>(null);
  const [isDialogOpen, setIsDialogOpen] = useState(false);

  const filteredShipments = mockShipments.filter((shipment) => {
    const matchesSearch =
      searchTerm === '' ||
      shipment.id.toLowerCase().includes(searchTerm.toLowerCase()) ||
      shipment.shipper.toLowerCase().includes(searchTerm.toLowerCase()) ||
      shipment.importer.toLowerCase().includes(searchTerm.toLowerCase()) ||
      shipment.commodity.toLowerCase().includes(searchTerm.toLowerCase());

    const matchesRisk = riskFilter === 'all' || shipment.riskLevel === riskFilter;
    const matchesStatus = statusFilter === 'all' || shipment.status === statusFilter;

    return matchesSearch && matchesRisk && matchesStatus;
  });

  const handleViewDetails = (shipment: ShipmentRecord) => {
    setSelectedShipment(shipment);
    setIsDialogOpen(true);
  };

  return (
    <div className="container mx-auto px-4 py-8" data-page="shipment-history">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold tracking-tight mb-2">Shipment History</h1>
          <p className="text-muted-foreground">
            Browse and review all assessed shipments
          </p>
        </div>

        {/* Filters */}
        <Card className="mb-6" data-section="filters">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Filter className="h-5 w-5" />
              Filters
            </CardTitle>
            <CardDescription>Search and filter shipment records</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4 md:grid-cols-4">
              <div className="md:col-span-2 relative">
                <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Search by ID, shipper, importer, or commodity..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-9"
                />
              </div>

              <Select value={riskFilter} onValueChange={setRiskFilter}>
                <SelectTrigger>
                  <SelectValue placeholder="Risk Level" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Risk Levels</SelectItem>
                  <SelectItem value="high">High Risk</SelectItem>
                  <SelectItem value="medium">Medium Risk</SelectItem>
                  <SelectItem value="low">Low Risk</SelectItem>
                </SelectContent>
              </Select>

              <Select value={statusFilter} onValueChange={setStatusFilter}>
                <SelectTrigger>
                  <SelectValue placeholder="Status" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Statuses</SelectItem>
                  <SelectItem value="approved">Approved</SelectItem>
                  <SelectItem value="rejected">Rejected</SelectItem>
                  <SelectItem value="under_review">Under Review</SelectItem>
                  <SelectItem value="pending">Pending</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </CardContent>
        </Card>

        {/* Results */}
        <Card data-section="shipment-table">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>Assessment Records</CardTitle>
                <CardDescription>
                  Showing {filteredShipments.length} of {mockShipments.length} shipments
                </CardDescription>
              </div>
              <Button variant="outline" size="sm" className="gap-2">
                <Download className="h-4 w-4" />
                Export
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
                  <TableHead>Importer</TableHead>
                  <TableHead>Commodity</TableHead>
                  <TableHead>Origin</TableHead>
                  <TableHead>Value</TableHead>
                  <TableHead>Risk Level</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Action</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredShipments.map((shipment) => (
                  <TableRow key={shipment.id}>
                    <TableCell className="font-mono text-sm">{shipment.id}</TableCell>
                    <TableCell className="text-sm">
                      {new Date(shipment.date).toLocaleDateString()}
                    </TableCell>
                    <TableCell className="max-w-[150px] truncate">{shipment.shipper}</TableCell>
                    <TableCell className="max-w-[150px] truncate">{shipment.importer}</TableCell>
                    <TableCell>{shipment.commodity}</TableCell>
                    <TableCell>{shipment.origin}</TableCell>
                    <TableCell>${shipment.value.toLocaleString()}</TableCell>
                    <TableCell>
                      <RiskBadge level={shipment.riskLevel} score={shipment.riskScore} showIcon={false} />
                    </TableCell>
                    <TableCell>
                      <Badge
                        variant={
                          shipment.status === 'approved'
                            ? 'secondary'
                            : shipment.status === 'rejected'
                            ? 'destructive'
                            : 'outline'
                        }
                        className="capitalize"
                      >
                        {shipment.status.replace('_', ' ')}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleViewDetails(shipment)}
                        className="gap-2"
                      >
                        <Eye className="h-4 w-4" />
                        View
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>

            {filteredShipments.length === 0 && (
              <div className="text-center py-12 text-muted-foreground">
                <p>No shipments found matching your filters</p>
              </div>
            )}
          </CardContent>
        </Card>
      </motion.div>

      {/* Details Dialog */}
      <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
        <DialogContent className="max-w-3xl max-h-[80vh] overflow-y-auto">
          {selectedShipment && (
            <>
              <DialogHeader>
                <DialogTitle className="flex items-center justify-between">
                  <span>{selectedShipment.id}</span>
                  <RiskBadge level={selectedShipment.riskLevel} score={selectedShipment.riskScore} />
                </DialogTitle>
                <DialogDescription>
                  Assessed on {new Date(selectedShipment.date).toLocaleDateString()}
                </DialogDescription>
              </DialogHeader>

              <div className="space-y-6 mt-4">
                {/* Shipment Info */}
                <div>
                  <h3 className="font-semibold mb-4">Shipment Information</h3>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <p className="text-muted-foreground">Shipper</p>
                      <p className="font-medium">{selectedShipment.shipper}</p>
                    </div>
                    <div>
                      <p className="text-muted-foreground">Importer</p>
                      <p className="font-medium">{selectedShipment.importer}</p>
                    </div>
                    <div>
                      <p className="text-muted-foreground">Commodity</p>
                      <p className="font-medium">{selectedShipment.commodity}</p>
                    </div>
                    <div>
                      <p className="text-muted-foreground">Origin</p>
                      <p className="font-medium">{selectedShipment.origin}</p>
                    </div>
                    <div>
                      <p className="text-muted-foreground">Declared Value</p>
                      <p className="font-medium">${selectedShipment.value.toLocaleString()}</p>
                    </div>
                    <div>
                      <p className="text-muted-foreground">Status</p>
                      <Badge
                        variant={
                          selectedShipment.status === 'approved'
                            ? 'secondary'
                            : selectedShipment.status === 'rejected'
                            ? 'destructive'
                            : 'outline'
                        }
                        className="capitalize"
                      >
                        {selectedShipment.status.replace('_', ' ')}
                      </Badge>
                    </div>
                  </div>
                </div>

                {/* Risk Flags */}
                {selectedShipment.flags.length > 0 && (
                  <div>
                    <h3 className="font-semibold mb-4">Risk Flags</h3>
                    <div className="space-y-2">
                      {selectedShipment.flags.map((flag, idx) => (
                        <div key={idx} className="p-3 rounded-lg bg-red-50 dark:bg-red-900/10 border border-red-200 dark:border-red-900 text-sm">
                          {flag}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {selectedShipment.flags.length === 0 && (
                  <div>
                    <h3 className="font-semibold mb-4">Risk Flags</h3>
                    <div className="p-3 rounded-lg bg-green-50 dark:bg-green-900/10 border border-green-200 dark:border-green-900 text-sm">
                      No risk flags detected
                    </div>
                  </div>
                )}
              </div>
            </>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}
