// Mock data for the proof-of-concept demo

export interface ShipmentRecord {
  id: string;
  date: string;
  shipper: string;
  importer: string;
  commodity: string;
  origin: string;
  value: number;
  riskLevel: 'high' | 'medium' | 'low';
  riskScore: number;
  flags: string[];
  status: 'pending' | 'approved' | 'rejected' | 'under_review';
}

export interface EntityProfile {
  id: string;
  name: string;
  type: 'shipper' | 'importer' | 'manufacturer';
  riskLevel: 'high' | 'medium' | 'low';
  riskScore: number;
  country: string;
  registrationDate: string;
  lastActivity: string;
  blacklistStatus: {
    list60B: boolean;
    approvedManufacturer: boolean;
    otherFlags: string[];
  };
  newsItems: NewsItem[];
  tradingPatterns: TradingPattern[];
}

export interface NewsItem {
  date: string;
  source: string;
  headline: string;
  sentiment: 'negative' | 'neutral' | 'positive';
  excerpt: string;
}

export interface TradingPattern {
  commodity: string;
  frequency: number;
  lastShipment: string;
  normalOrigins: string[];
}

export const mockShipments: ShipmentRecord[] = [
  {
    id: 'SHP-2024-001',
    date: '2024-11-15',
    shipper: 'Global Trade Corp',
    importer: 'Mexico Imports SA',
    commodity: 'Soccer Balls',
    origin: 'China',
    value: 45000,
    riskLevel: 'high',
    riskScore: 87,
    flags: ['Commodity Origin Mismatch', 'Unusual Route'],
    status: 'under_review'
  },
  {
    id: 'SHP-2024-002',
    date: '2024-11-14',
    shipper: 'Pacific Logistics Ltd',
    importer: 'Automotive Parts MX',
    commodity: 'Auto Parts',
    origin: 'Japan',
    value: 125000,
    riskLevel: 'low',
    riskScore: 15,
    flags: [],
    status: 'approved'
  },
  {
    id: 'SHP-2024-003',
    date: '2024-11-14',
    shipper: 'Eastern Trading Co',
    importer: 'TechnoMex Solutions',
    commodity: 'Electronics',
    origin: 'Taiwan',
    value: 89000,
    riskLevel: 'low',
    riskScore: 22,
    flags: [],
    status: 'approved'
  },
  {
    id: 'SHP-2024-004',
    date: '2024-11-13',
    shipper: 'Flores International',
    importer: 'Decoraciones Mexico',
    commodity: 'Hibiscus Flowers',
    origin: 'Colombia',
    value: 12000,
    riskLevel: 'medium',
    riskScore: 58,
    flags: ['Origin Anomaly - Expected Nigeria'],
    status: 'under_review'
  },
  {
    id: 'SHP-2024-005',
    date: '2024-11-13',
    shipper: 'Textiles Global',
    importer: 'Fashion MX',
    commodity: 'Textiles',
    origin: 'India',
    value: 67000,
    riskLevel: 'low',
    riskScore: 18,
    flags: [],
    status: 'approved'
  },
  {
    id: 'SHP-2024-006',
    date: '2024-11-12',
    shipper: 'Rapid Shift Logistics',
    importer: 'Juguetes Mexico',
    commodity: 'Toys',
    origin: 'Vietnam',
    value: 34000,
    riskLevel: 'medium',
    riskScore: 64,
    flags: ['Shipper on 60B List', 'Unusual Commodity Change'],
    status: 'rejected'
  },
  {
    id: 'SHP-2024-007',
    date: '2024-11-12',
    shipper: 'Euro Shipping AG',
    importer: 'Maquinaria Industrial MX',
    commodity: 'Machinery',
    origin: 'Germany',
    value: 245000,
    riskLevel: 'low',
    riskScore: 12,
    flags: [],
    status: 'approved'
  },
  {
    id: 'SHP-2024-008',
    date: '2024-11-11',
    shipper: 'Asia Commerce Ltd',
    importer: 'ElectroMex SA',
    commodity: 'Consumer Electronics',
    origin: 'South Korea',
    value: 98000,
    riskLevel: 'low',
    riskScore: 20,
    flags: [],
    status: 'approved'
  }
];

export const mockEntities: EntityProfile[] = [
  {
    id: 'ENT-001',
    name: 'Global Trade Corp',
    type: 'shipper',
    riskLevel: 'high',
    riskScore: 87,
    country: 'China',
    registrationDate: '2018-03-15',
    lastActivity: '2024-11-15',
    blacklistStatus: {
      list60B: false,
      approvedManufacturer: true,
      otherFlags: ['Previous customs violations']
    },
    newsItems: [
      {
        date: '2024-09-12',
        source: 'Trade Compliance News',
        headline: 'Global Trade Corp faces customs investigation in Brazil',
        sentiment: 'negative',
        excerpt: 'Authorities have launched an investigation into alleged documentation irregularities...'
      },
      {
        date: '2024-06-05',
        source: 'Business Wire',
        headline: 'Company expands operations to Southeast Asia',
        sentiment: 'neutral',
        excerpt: 'Global Trade Corp announces new distribution centers in Thailand and Vietnam...'
      }
    ],
    tradingPatterns: [
      {
        commodity: 'Auto Parts',
        frequency: 45,
        lastShipment: '2024-10-28',
        normalOrigins: ['China', 'Japan']
      },
      {
        commodity: 'Soccer Balls',
        frequency: 2,
        lastShipment: '2024-11-15',
        normalOrigins: ['Pakistan']
      }
    ]
  },
  {
    id: 'ENT-002',
    name: 'Rapid Shift Logistics',
    type: 'shipper',
    riskLevel: 'high',
    riskScore: 92,
    country: 'Panama',
    registrationDate: '2020-08-22',
    lastActivity: '2024-11-12',
    blacklistStatus: {
      list60B: true,
      approvedManufacturer: false,
      otherFlags: ['Tax evasion investigation', 'Shell company indicators']
    },
    newsItems: [
      {
        date: '2024-10-18',
        source: 'Latin America Financial Times',
        headline: 'Panama authorities investigate Rapid Shift for tax fraud',
        sentiment: 'negative',
        excerpt: 'The company is under investigation for alleged tax evasion schemes involving offshore accounts...'
      },
      {
        date: '2024-08-02',
        source: 'Global Trade Alert',
        headline: 'Rapid Shift linked to suspicious cargo incidents',
        sentiment: 'negative',
        excerpt: 'Multiple customs agencies report irregularities in shipments handled by the logistics firm...'
      }
    ],
    tradingPatterns: [
      {
        commodity: 'Toys',
        frequency: 8,
        lastShipment: '2024-11-12',
        normalOrigins: ['China', 'Vietnam']
      },
      {
        commodity: 'Electronics',
        frequency: 3,
        lastShipment: '2024-09-20',
        normalOrigins: ['China']
      }
    ]
  },
  {
    id: 'ENT-003',
    name: 'Pacific Logistics Ltd',
    type: 'shipper',
    riskLevel: 'low',
    riskScore: 15,
    country: 'Japan',
    registrationDate: '2010-05-10',
    lastActivity: '2024-11-14',
    blacklistStatus: {
      list60B: false,
      approvedManufacturer: true,
      otherFlags: []
    },
    newsItems: [
      {
        date: '2024-10-05',
        source: 'Asian Business Review',
        headline: 'Pacific Logistics wins excellence award for compliance',
        sentiment: 'positive',
        excerpt: 'The company has been recognized for its outstanding track record in international trade compliance...'
      },
      {
        date: '2024-07-15',
        source: 'Logistics Today',
        headline: 'Pacific Logistics expands green shipping initiatives',
        sentiment: 'positive',
        excerpt: 'New environmentally-friendly fleet reduces carbon emissions by 30%...'
      }
    ],
    tradingPatterns: [
      {
        commodity: 'Auto Parts',
        frequency: 120,
        lastShipment: '2024-11-14',
        normalOrigins: ['Japan', 'South Korea']
      },
      {
        commodity: 'Machinery',
        frequency: 45,
        lastShipment: '2024-11-10',
        normalOrigins: ['Japan', 'Germany']
      }
    ]
  },
  {
    id: 'ENT-004',
    name: 'Flores International',
    type: 'shipper',
    riskLevel: 'medium',
    riskScore: 58,
    country: 'Colombia',
    registrationDate: '2015-11-03',
    lastActivity: '2024-11-13',
    blacklistStatus: {
      list60B: false,
      approvedManufacturer: true,
      otherFlags: ['Minor documentation issues']
    },
    newsItems: [
      {
        date: '2024-08-20',
        source: 'Agriculture Trade News',
        headline: 'Flores International expands flower export operations',
        sentiment: 'positive',
        excerpt: 'Company increases production capacity to meet growing international demand...'
      }
    ],
    tradingPatterns: [
      {
        commodity: 'Hibiscus Flowers',
        frequency: 24,
        lastShipment: '2024-11-13',
        normalOrigins: ['Colombia', 'Ecuador']
      },
      {
        commodity: 'Roses',
        frequency: 56,
        lastShipment: '2024-11-12',
        normalOrigins: ['Colombia']
      }
    ]
  }
];

export const dashboardStats = {
  totalAssessments: 1247,
  highRiskAlerts: 34,
  pendingReview: 12,
  avgProcessingTime: '4.2 min',
  riskDistribution: [
    { name: 'Low Risk', value: 892, color: '#10b981' },
    { name: 'Medium Risk', value: 321, color: '#f59e0b' },
    { name: 'High Risk', value: 34, color: '#ef4444' }
  ],
  weeklyTrend: [
    { day: 'Mon', assessments: 45, alerts: 3 },
    { day: 'Tue', assessments: 52, alerts: 5 },
    { day: 'Wed', assessments: 48, alerts: 2 },
    { day: 'Thu', assessments: 61, alerts: 7 },
    { day: 'Fri', assessments: 58, alerts: 4 },
    { day: 'Sat', assessments: 23, alerts: 1 },
    { day: 'Sun', assessments: 19, alerts: 0 }
  ],
  topFlags: [
    { flag: 'Commodity Origin Mismatch', count: 12 },
    { flag: 'Shipper on 60B List', count: 8 },
    { flag: 'Unusual Route', count: 6 },
    { flag: 'Documentation Issues', count: 5 },
    { flag: 'Pattern Anomaly', count: 3 }
  ]
};

// Hardcoded AI assessment response for new shipment
export const generateAIAssessment = (shipmentData: Record<string, string>) => {
  const responses: Record<string, {
    riskLevel: 'high' | 'medium' | 'low';
    riskScore: number;
    flags: string[];
    entityChecks: Record<string, string>;
    recommendations: string[];
    patternAnalysis: string;
    aiInsights: string;
  }> = {
    'soccer-balls-china': {
      riskLevel: 'high',
      riskScore: 87,
      flags: [
        'Commodity Origin Mismatch - 70% of soccer balls are manufactured in Pakistan',
        'Unusual shipping route detected',
        'Price point below market average'
      ],
      entityChecks: {
        shipper: 'Clean - No blacklist entries',
        importer: 'Warning - Recently changed business address',
        manufacturer: 'Not on approved manufacturer list for this commodity'
      },
      recommendations: [
        'Request additional documentation on manufacturing origin',
        'Verify importer\'s business registration and address change',
        'Consider physical inspection of cargo',
        'Require manufacturer certification'
      ],
      patternAnalysis: 'Shipper typically handles auto parts (95% of shipments). This commodity represents significant deviation from normal trading pattern.',
      aiInsights: 'This shipment exhibits multiple red flags that warrant careful review. The combination of commodity-origin mismatch, unusual shipper behavior, and lack of manufacturer certification suggests elevated risk.'
    },
    'default': {
      riskLevel: 'medium',
      riskScore: 45,
      flags: [
        'Standard commodity routing',
        'All parties cleared in basic checks'
      ],
      entityChecks: {
        shipper: 'Clean - No issues found',
        importer: 'Clean - No issues found',
        manufacturer: 'Verified'
      },
      recommendations: [
        'Proceed with standard documentation review',
        'No additional inspection required'
      ],
      patternAnalysis: 'Trading pattern consistent with historical data.',
      aiInsights: 'This shipment appears standard with no significant risk indicators detected.'
    }
  };

  // Simulate AI analysis based on input
  const key = `${shipmentData.commodity?.toLowerCase().replace(/\s+/g, '-')}-${shipmentData.origin?.toLowerCase()}`;
  return responses[key] || responses['default'];
};
