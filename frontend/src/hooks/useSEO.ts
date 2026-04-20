import { useEffect } from 'react'

interface SEOProps {
  title: string
  description: string
  canonical?: string
  ogTitle?: string
  ogDescription?: string
  ogType?: string
  noindex?: boolean
}

export function useSEO({
  title,
  description,
  canonical,
  ogTitle,
  ogDescription,
  ogType = 'website',
  noindex = false,
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
    setMeta('og:title', ogTitle || title, true)
    setMeta('og:description', ogDescription || description, true)
    setMeta('og:type', ogType, true)
    setMeta('og:site_name', 'VeritasAI', true)
    setMeta('twitter:card', 'summary_large_image')
    setMeta('twitter:title', ogTitle || title)
    setMeta('twitter:description', ogDescription || description)

    if (canonical) {
      let link = document.querySelector('link[rel="canonical"]') as HTMLLinkElement | null
      if (!link) {
        link = document.createElement('link')
        link.rel = 'canonical'
        document.head.appendChild(link)
      }
      link.href = canonical
    }

    return () => {
      document.title = 'VeritasAI — AI Content Detection'
    }
  }, [title, description, canonical, ogTitle, ogDescription, ogType, noindex])
}
