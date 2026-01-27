export interface User {
  id: number;
  first_name: string;
  age: number;
  bio?: string;
  work?: string;
  distance_km?: number;
  photos: { url: string }[];
}
