/**
 * Project timeline tab with activity feed and novelty risk trend chart.
 */

import type { ReactElement } from "react";
import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { ProjectRiskTrendPoint, ProjectTimelineEvent } from "../../types/project";

type TimelineTabProps = {
  events: ProjectTimelineEvent[];
  riskTrend: ProjectRiskTrendPoint[];
};

type RiskDotProps = {
  cx?: number;
  cy?: number;
  payload?: ProjectRiskTrendPoint;
};

function renderRiskDot(dotProps: RiskDotProps): ReactElement<SVGElement> {
  const pointRisk = dotProps.payload?.overall_risk ?? "UNKNOWN";
  return (
    <circle
      cx={dotProps.cx}
      cy={dotProps.cy}
      r={4}
      fill={riskColor(pointRisk)}
      stroke="#ffffff"
      strokeWidth={2}
    />
  ) as ReactElement<SVGElement>;
}

function eventIcon(eventType: ProjectTimelineEvent["event_type"]): string {
  if (eventType === "SEARCH") {
    return "S";
  }
  if (eventType === "ANALYSIS") {
    return "AI";
  }
  return "PDF";
}

function riskColor(risk: ProjectRiskTrendPoint["overall_risk"]): string {
  if (risk === "HIGH") {
    return "#C00000";
  }
  if (risk === "MEDIUM") {
    return "#ED7D31";
  }
  if (risk === "LOW") {
    return "#548235";
  }
  return "#5580C8";
}

export default function TimelineTab({ events, riskTrend }: Readonly<TimelineTabProps>): ReactElement {
  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-sm font-semibold uppercase tracking-widest text-primary">Project Timeline</h3>
        <div className="mt-4 space-y-4">
          {events.length === 0 ? (
            <p className="rounded-xl bg-surface p-4 text-sm text-text-secondary">No timeline events yet.</p>
          ) : (
            events.map((event) => (
              <div key={`${event.event_type}-${event.timestamp}-${event.title}`} className="flex gap-3">
                <div className="mt-1 inline-flex h-8 min-w-8 items-center justify-center rounded-full bg-primary text-xs font-bold text-white">
                  {eventIcon(event.event_type)}
                </div>
                <div className="flex-1 rounded-xl border border-slate-200 bg-white p-3">
                  <p className="text-xs text-text-secondary">{new Date(event.timestamp).toLocaleString()}</p>
                  <p className="text-sm font-semibold text-text-primary">{event.title}</p>
                  <p className="mt-1 text-sm text-text-secondary">{event.summary}</p>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      <div className="rounded-2xl border border-slate-200 bg-white p-4">
        <h3 className="text-sm font-semibold uppercase tracking-widest text-primary">Novelty Risk Trend</h3>
        {riskTrend.length === 0 ? (
          <p className="mt-3 rounded-xl bg-surface p-4 text-sm text-text-secondary">Risk trend will appear after completed sessions.</p>
        ) : (
          <div className="mt-4 h-72">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={riskTrend} margin={{ top: 10, right: 20, bottom: 20, left: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" />
                <XAxis
                  dataKey="session_date"
                  tickFormatter={(value: string) => new Date(value).toLocaleDateString()}
                  stroke="#595959"
                />
                <YAxis domain={[0, 1]} stroke="#595959" />
                <Tooltip
                  formatter={(value: number, _name, payload) => {
                    const risk = String(payload?.payload?.overall_risk ?? "UNKNOWN");
                    return [`${Number(value).toFixed(3)} (${risk})`, "Avg Composite Score"];
                  }}
                  labelFormatter={(label: string) => new Date(label).toLocaleDateString()}
                />
                <Line
                  type="monotone"
                  dataKey="avg_composite_score"
                  stroke="#003399"
                  strokeWidth={2.5}
                  dot={renderRiskDot}
                  activeDot={{ r: 6 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>
    </div>
  );
}
