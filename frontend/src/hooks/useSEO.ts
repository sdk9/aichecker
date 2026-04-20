import { useEffect } from 'react'

interface SEOProps {
  title: string
  description: string
  canonical?: string
  keywords?: string
  ogTitle?: string
  ogDescription?: string
  ogImage?: string
  ogType?: string
  noindex?: boolean
  schema?: object | object[]
}

const BASE_OG_IMAGE = 'https://veritasartificialis.com/og-image.svg'

export function useSEO({
  title,
  description,
  canonical,
  keywords,
  ogTitle,
  ogDescription,
  ogImage = BASE_OG_IMAGE,
  ogType = 'website',
  noindex = false,
  schema,
}: SEOProps) {
  useEffect(() => {
    document.title = title

    const setMeta = (name: string, content: string, property = false) => {
      const attr = property ? 'property' : 'name'
      let el = document.querySelector(`meta[${attr}="${name}"]`) as HTMLMetaElement | null
      if (!el) {
        el = document.createElement('meta')
        el.setAttribute(attr, name)
        document.head.appendChild(el)
      }
      el.content = content
    }

    setMeta('description', description)
    setMeta('robots', noindex ? 'noindex,nofollow' : 'index,follow')
    if (keywords) setMeta('keywords', keywords)

    setMeta('og:title', ogTitle || title, true)
    setMeta('og:description', ogDescription || description, true)
    setMeta('og:type', ogType, true)
    setMeta('og:site_name', 'VeritasAI', true)
    if (ogImage) setMeta('og:image', ogImage, true)

    setMeta('twitter:card', 'summary_large_image')
    setMeta('twitter:title', ogTitle || title)
    setMeta('twitter:description', ogDescription || description)
    if (ogImage) setMeta('twitter:image', ogImage)

    if (canonical) {
      let link = document.querySelector('link[rel="canonical"]') as HTMLLinkElement | null
      if (!link) {
        link = document.createElement('link')
        link.rel = 'canonical'
        document.head.appendChild(link)
      }
      link.href = canonical
    }

    if (schema) {
      const id = `seo-schema-${Math.random().toString(36).slice(2)}`
      const script = document.createElement('script')
      script.type = 'application/ld+json'
      script.id = id
      script.text = JSON.stringify(schema)
      document.head.appendChild(script)
      return () => {
        document.title = 'VeritasAI — Free AI Content Detector'
        document.getElementById(id)?.remove()
      }
    }

    return () => {
      document.title = 'VeritasAI — Free AI Content Detector'
    }
  }, [title, description, canonical, keywords, ogTitle, ogDescription, ogImage, ogType, noindex])
}
