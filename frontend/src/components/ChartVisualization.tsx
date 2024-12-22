import React, { useEffect, useRef } from 'react';
import * as d3 from 'd3';
import { BirthChart } from '../types/chart';

interface ChartVisualizationProps {
  chart: BirthChart;
}

const ChartVisualization: React.FC<ChartVisualizationProps> = ({ chart }) => {
  const svgRef = useRef<SVGSVGElement>(null);

  useEffect(() => {
    if (!svgRef.current || !chart) return;

    const svg = d3.select(svgRef.current);
    if (!svg) return;

    const width = 800;
    const height = 800;
    const margin = 40;
    const centerX = width / 2;
    const centerY = height / 2;

    // Clear previous content
    svg.selectAll("*").remove();

    // Set up the chart container
    svg
      .attr("width", width)
      .attr("height", height)
      .attr("viewBox", `0 0 ${width} ${height}`);

    // Draw the main square
    const mainSquare = svg
      .append("rect")
      .attr("x", margin)
      .attr("y", margin)
      .attr("width", width - 2 * margin)
      .attr("height", height - 2 * margin)
      .attr("fill", "none")
      .attr("stroke", "#000")
      .attr("stroke-width", 2);

    // Draw inner squares for houses
    const innerSquareSize = (width - 4 * margin) / 3;
    for (let i = 0; i < 3; i++) {
      for (let j = 0; j < 3; j++) {
        svg
          .append("rect")
          .attr("x", margin + i * innerSquareSize)
          .attr("y", margin + j * innerSquareSize)
          .attr("width", innerSquareSize)
          .attr("height", innerSquareSize)
          .attr("fill", "none")
          .attr("stroke", "#000");
      }
    }

    // Add planetary positions
    if (chart.planetary_positions) {
      Object.entries(chart.planetary_positions).forEach(([planet, position], index) => {
        const angle = position.longitude;
        const radius = (width - 4 * margin) / 2;
        const x = centerX + radius * Math.cos((angle * Math.PI) / 180);
        const y = centerY + radius * Math.sin((angle * Math.PI) / 180);

        svg
          .append("circle")
          .attr("cx", x)
          .attr("cy", y)
          .attr("r", 5)
          .attr("fill", "#000");

        svg
          .append("text")
          .attr("x", x)
          .attr("y", y - 10)
          .attr("text-anchor", "middle")
          .attr("dominant-baseline", "middle")
          .text(planet);
      });
    }

    // Add house cusps
    if (chart.houses && chart.houses.cusps) {
      chart.houses.cusps.forEach((cusp, index) => {
        const angle = cusp;
        const radius = width / 2 - margin;
        const x1 = centerX;
        const y1 = centerY;
        const x2 = centerX + radius * Math.cos((angle * Math.PI) / 180);
        const y2 = centerY + radius * Math.sin((angle * Math.PI) / 180);

        svg
          .append("line")
          .attr("x1", x1)
          .attr("y1", y1)
          .attr("x2", x2)
          .attr("y2", y2)
          .attr("stroke", "#000")
          .attr("stroke-dasharray", "5,5");

        svg
          .append("text")
          .attr("x", x2 + 10 * Math.cos((angle * Math.PI) / 180))
          .attr("y", y2 + 10 * Math.sin((angle * Math.PI) / 180))
          .attr("text-anchor", "middle")
          .attr("dominant-baseline", "middle")
          .text(index + 1);
      });
    }

    // Add aspects
    if (chart.aspects) {
      chart.aspects.forEach((aspect) => {
        const planet1Pos = chart.planetary_positions[aspect.planet1];
        const planet2Pos = chart.planetary_positions[aspect.planet2];

        if (planet1Pos && planet2Pos) {
          const angle1 = planet1Pos.longitude;
          const angle2 = planet2Pos.longitude;
          const radius = (width - 6 * margin) / 2;

          const x1 = centerX + radius * Math.cos((angle1 * Math.PI) / 180);
          const y1 = centerY + radius * Math.sin((angle1 * Math.PI) / 180);
          const x2 = centerX + radius * Math.cos((angle2 * Math.PI) / 180);
          const y2 = centerY + radius * Math.sin((angle2 * Math.PI) / 180);

          svg
            .append("line")
            .attr("x1", x1)
            .attr("y1", y1)
            .attr("x2", x2)
            .attr("y2", y2)
            .attr("stroke", aspect.is_major ? "#f00" : "#999")
            .attr("stroke-width", aspect.is_major ? 2 : 1);
        }
      });
    }
  }, [chart]);

  return (
    <div className="w-full max-w-4xl mx-auto">
      <svg ref={svgRef} className="w-full h-auto" />
    </div>
  );
};

export default ChartVisualization;
