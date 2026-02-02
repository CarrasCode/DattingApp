export interface PublicProfile {
  id: string;
  first_name: string;
  bio: string | null;
  work: string | null;
  age: string;
  gender: IGender;
  photos: IPhoto[];
  distance_km: string;
}

export interface IGender {
  gender: 'M' | 'F' | 'NB' | 'O';
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
  gender_preference: 'M' | 'F' | 'A' | null;
  max_distance: number | null;
  min_age: number | null;
  max_age: number | null;
  location: { lat: number; lng: number } | null;
}
export interface IEditProfile {
  first_name?: string;
  bio?: string | null;
  work?: string | null;
  gender?: IGender;
  birth_date?: string;
  gender_preference?: 'M' | 'F' | 'A' | null;
  max_distance?: number | null;
  min_age?: number | null;
  max_age?: number | null;
  latitude?: number | null;
  longitude?: number | null;
}

export interface IPhoto {
  id: string;
  image: string;
  is_main: boolean;
  caption: string | null;
}

export interface PhotoUpload {
  image: File;
  is_main: boolean;
  caption: string | null;
}
