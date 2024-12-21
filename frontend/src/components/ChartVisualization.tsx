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
          .attr("stroke", "#000")
          .attr("stroke-width", 1);
      }
    }

    // Place planets in their respective houses
    Object.entries(chart.planetary_positions).forEach(([planet, position]) => {
      const house = Math.floor(position.longitude / 30) + 1;
      const houseX = margin + ((house - 1) % 3) * innerSquareSize;
      const houseY = margin + Math.floor((house - 1) / 3) * innerSquareSize;

      // Add planet symbol
      svg
        .append("text")
        .attr("x", houseX + innerSquareSize / 2)
        .attr("y", houseY + innerSquareSize / 2)
        .attr("text-anchor", "middle")
        .attr("dominant-baseline", "middle")
        .attr("font-size", "16px")
        .text(planet);

      // Add degree
      svg
        .append("text")
        .attr("x", houseX + innerSquareSize / 2)
        .attr("y", houseY + innerSquareSize / 2 + 20)
        .attr("text-anchor", "middle")
        .attr("dominant-baseline", "middle")
        .attr("font-size", "12px")
        .text(`${Math.floor(position.longitude % 30)}°`);
    });

    // Add house numbers
    for (let i = 1; i <= 12; i++) {
      const x = margin + ((i - 1) % 3) * innerSquareSize;
      const y = margin + Math.floor((i - 1) / 3) * innerSquareSize;

      svg
        .append("text")
        .attr("x", x + 10)
        .attr("y", y + 20)
        .attr("font-size", "14px")
        .text(i.toString());
    }

  }, [chart]);

  return (
    <div className="w-full max-w-4xl mx-auto">
      <svg ref={svgRef} className="w-full h-auto" />
    </div>
  );
};

export default ChartVisualization;
