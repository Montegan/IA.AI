import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useState } from "react";
import { auth, provider } from "@/firebase_config";
import { signInWithPopup, signOut } from "firebase/auth";
import { Link } from "react-router-dom";

export function Sighupform() {
  const [email, setEmail] = useState();

  const signinUser = () => {
    signInWithPopup(auth, provider).then((data) => {
      setEmail(data.user.email);
    });
  };

  return (
    <Card className="mx-auto max-w-sm">
      <CardHeader>
        <CardTitle className="text-2xl">Login</CardTitle>
        <CardDescription>
          Enter your email below to login to your account
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="grid gap-4">
          <div className="grid gap-2">
            <Label htmlFor="email">Email</Label>
            <Input
              id="email"
              type="email"
              placeholder="m@example.com"
              value={email}
              onChange={(e) => {
                console.log(e.target.value);
                setEmail(e.target.value);
              }}
              required
            />
          </div>
          <div className="grid gap-2">
            <div className="flex items-center">
              <Label htmlFor="password">Password</Label>
              <a href="#" className="ml-auto inline-block text-sm underline">
                Forgot your password?
              </a>
            </div>
            <Input id="password" type="password" required />
          </div>
          <Button type="submit" className="w-full">
            Signup
          </Button>
          <Button variant="outline" className="w-full" onClick={signinUser}>
            Signup with Google
          </Button>
        </div>
        <div className="mt-4 text-center text-sm">
          have an account?{" "}
          <Link to="/login" className="underline">
            Login
          </Link>
        </div>
      </CardContent>
    </Card>
  );
}
