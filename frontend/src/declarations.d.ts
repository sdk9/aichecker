declare module "*.css" {}

interface ImportMeta {
  env: {
    VITE_API_URL?: string
    [key: string]: string | undefined
  }
}
