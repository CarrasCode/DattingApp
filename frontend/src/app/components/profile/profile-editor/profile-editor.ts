import { Component, inject } from '@angular/core';
import { FormControl, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { UserService } from '../../../services/user-service';

@Component({
  selector: 'app-profile-editor',
  imports: [ReactiveFormsModule],
  templateUrl: './profile-editor.html',
  styleUrl: './profile-editor.scss',
})
export class ProfileEditor {
  userService = inject(UserService);
  profile = this.userService.currentUser;

  profileEditor = new FormGroup({
    first_name: new FormControl(this.profile()?.first_name, Validators.required),
    bio: new FormControl(this.profile()?.bio),
    work: new FormControl(this.profile()?.work),
    birth_date: new FormControl(this.profile()?.birth_date),
    gender: new FormControl(this.profile()?.gender, [Validators.required]),
    gender_preference: new FormControl(this.profile()?.gender_preference, [Validators.required]),
    max_distance: new FormControl(this.profile()?.max_distance, [Validators.required]),
    min_age: new FormControl(this.profile()?.min_age, [Validators.min(18), Validators.required]),
    max_age: new FormControl(this.profile()?.max_age, [Validators.max(100), Validators.required]),
  });

  onSubmit() {
    console.log(this.profileEditor.value);
    // this.userService.updateProfile(this.profileEditor.value);
  }
}
