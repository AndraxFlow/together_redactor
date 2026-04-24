// import { useNavigate } from "react-router-dom"
// import { register, login } from "../api/auth"
// import { RegisterForm } from "../components/RegisterForm"
// import { useAuth } from "../auth/useAuth"

// export default function RegisterPage() {
//   const navigate = useNavigate()
//   const { login: saveToken } = useAuth()

//   async function handleRegister(email: string, password: string) {
//     await register(email, password)

//     const data = await login(email, password)

//     saveToken(data.access_token)

//     navigate("/documents")
//   }

//   return <RegisterForm onSubmit={handleRegister} />
// }