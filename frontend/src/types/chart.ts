export interface Location {
  latitude: number;
  longitude: number;
  altitude: number;
}

export interface PlanetaryPosition {
  longitude: number;
  latitude?: number;
  distance?: number;
  speed?: number;
}

export interface HouseData {
  cusps: number[];
  ascendant: number;
  midheaven: number;
  armc: number;
  vertex: number;
}

export interface Aspect {
  planet1: string;
  planet2: string;
  aspect: string;
  angle: number;
  orb: number;
  is_major: boolean;
  is_applying: boolean;
}

export interface NakshatraData {
  number: number;
  name: string;
  lord: string;
  pada: number;
  degrees_traversed: number;
  total_degrees: number;
}

export interface BirthChart {
  date_time: string;
  location: Location;
  ayanamsa: number;
  house_system: string;
  planetary_positions: Record<string, PlanetaryPosition>;
  houses: HouseData;
  aspects: Aspect[];
  nakshatras: Record<string, NakshatraData>;
}
