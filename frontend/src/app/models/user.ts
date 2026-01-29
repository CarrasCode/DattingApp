export interface User {
  id: string;
  first_name: string;
  bio: string | null;
  work: string | null;
  age: string;
  gender: IGender;
  photos: IPhoto[];
  distance_km: string;
}

interface IGender {
  gender: 'M' | 'F' | 'NB' | 'O';
}
interface IGenderPref {
  gender: 'M' | 'F' | 'A';
}
export interface ICurrentProfile {
  id: string;
  first_name: string;
  bio: string | null;
  work: string | null;
  age: string;
  gender: IGender;
  photos: IPhoto[];
  email: string;
  birth_date: string;
  gender_preference: IGenderPref | null;
  max_distance: number | null;
  min_age: number | null;
  max_age: number | null;
  location: string;
}
export interface IEditProfile {
  first_name: string;
  bio: string | null;
  work: string | null;
  gender: IGender;
  birth_date: string;
  gender_preference: IGenderPref | null;
  max_distance: number | null;
  min_age: number | null;
  max_age: number | null;
}

export interface IPhoto {
  id: string;
  image: string;
  is_main: boolean | null;
  caption: string | null;
}
