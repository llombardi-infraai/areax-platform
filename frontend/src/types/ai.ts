export interface Blueprint {
  id: string
  version: '1.0'
  createdAt: string
  updatedAt: string
  createdBy: string
  business: {
    name: string
    industry: string
    description: string
    targetCustomers: string
    revenueModel: string
    teamSize: string
  }
  currentState: {
    tools: string[]
    painPoints: string[]
    strengths: string[]
  }
  goals: {
    shortTerm: GoalPeriod
    mediumTerm: GoalPeriod
    longTerm: GoalPeriod
  }
  recommendations: Recommendation[]
  roadmap: RoadmapPhase[]
  risks: Risk[]
  checklist: ChecklistItem[]
}

interface GoalPeriod {
  objectives: string[]
  successMetrics: string[]
}

interface Recommendation {
  category: string
  priority: 'critical' | 'high' | 'medium' | 'low'
  systemType: string
  description: string
  businessCase: string
  estimatedTimeline: string
  prerequisites: string[]
}

interface RoadmapPhase {
  phase: number
  name: string
  description: string
  durationWeeks: number
  systems: string[]
  milestones: Milestone[]
  dependencies: number[]
}

interface Milestone {
  name: string
  description: string
  deliverables: string[]
}

interface Risk {
  category: 'security' | 'operational' | 'technical' | 'financial'
  severity: 'low' | 'medium' | 'high' | 'critical'
  description: string
  mitigation: string
}

interface ChecklistItem {
  id: string
  title: string
  category: string
  priority: 'critical' | 'high' | 'medium' | 'low'
  completed: boolean
  completedAt?: string
}
