import { Title, Container, Main } from '../../components'
import styles from './styles.module.css'
import MetaTags from 'react-meta-tags'
import { useState, useEffect } from 'react'

const Technologies = () => {
  const [visibleTechs, setVisibleTechs] = useState([])
  const [hoveredTech, setHoveredTech] = useState(null)

  const technologies = [
    {
      name: 'Python',
      icon: '🐍',
      description: 'Мощный язык программирования для backend разработки',
      color: '#3776ab',
      level: 95
    },
    {
      name: 'Django',
      icon: '🎸',
      description: 'Веб-фреймворк для быстрой разработки',
      color: '#092e20',
      level: 90
    },
    {
      name: 'Django REST Framework',
      icon: '⚡',
      description: 'Инструментарий для создания Web API',
      color: '#ff1709',
      level: 85
    },
    {
      name: 'Djoser',
      icon: '🔐',
      description: 'Библиотека для аутентификации пользователей',
      color: '#17a2b8',
      level: 80
    },
    {
      name: 'React',
      icon: '⚛️',
      description: 'JavaScript библиотека для создания пользовательских интерфейсов',
      color: '#61dafb',
      level: 88
    },
    {
      name: 'Docker',
      icon: '🐳',
      description: 'Платформа для контейнеризации приложений',
      color: '#2496ed',
      level: 75
    }
  ]

  useEffect(() => {
    technologies.forEach((_, index) => {
      setTimeout(() => {
        setVisibleTechs(prev => [...prev, index])
      }, index * 200)
    })
  }, [])

  const [codeAnimation, setCodeAnimation] = useState('')
  const codeSnippets = [
    'from django.db import models',
    'class Recipe(models.Model):',
    '    name = models.CharField(max_length=200)',
    '    description = models.TextField()',
    '    def __str__(self):',
    '        return self.name'
  ]

  useEffect(() => {
    let currentLine = 0
    const codeTimer = setInterval(() => {
      if (currentLine < codeSnippets.length) {
        setCodeAnimation(prev => prev + codeSnippets[currentLine] + '\n')
        currentLine++
      } else {
        setCodeAnimation('')
        currentLine = 0
      }
    }, 1000)

    return () => clearInterval(codeTimer)
  }, [])

  return <Main>
    <MetaTags>
      <title>Технологии - FoodGram</title>
      <meta name="description" content="Фудграм - Технологии проекта" />
      <meta property="og:title" content="Технологии" />
    </MetaTags>

    <Container>
      <h1 className={styles.title} style={{
        background: 'linear-gradient(45deg, #667eea, #764ba2)',
        WebkitBackgroundClip: 'text',
        WebkitTextFillColor: 'transparent',
        backgroundClip: 'text',
        textAlign: 'center',
        position: 'relative'
      }}>
        Технологии
        <span style={{
          position: 'absolute',
          top: '-10px',
          right: '-20px',
          fontSize: '24px',
          animation: 'bounce 2s infinite'
        }}>🚀</span>
      </h1>

      <div style={{
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        color: 'white',
        padding: '20px',
        borderRadius: '15px',
        margin: '20px 0',
        textAlign: 'center',
        position: 'relative',
        overflow: 'hidden'
      }}>
        <div style={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'url("data:image/svg+xml,%3Csvg width="20" height="20" xmlns="http://www.w3.org/2000/svg"%3E%3Cdefs%3E%3Cpattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse"%3E%3Cpath d="M 20 0 L 0 0 0 20" fill="none" stroke="rgba(255,255,255,0.1)" stroke-width="1"/%3E%3C/pattern%3E%3C/defs%3E%3Crect width="100%25" height="100%25" fill="url(%23grid)" /%3E%3C/svg%3E")',
          opacity: 0.3
        }}></div>
        <h2 style={{
          margin: '0 0 15px 0',
          position: 'relative',
          zIndex: 1,
          fontSize: '24px'
        }}>
          💻 Стек технологий проекта
        </h2>
        <p style={{
          margin: 0,
          position: 'relative',
          zIndex: 1,
          fontSize: '16px',
          opacity: 0.9
        }}>
          Современные инструменты для создания надежного веб-приложения
        </p>
      </div>

      <div className={styles.content}>
        <div>
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
            gap: '20px',
            margin: '30px 0'
          }}>
            {technologies.map((tech, index) => (
              <div
                key={tech.name}
                style={{
                  background: visibleTechs.includes(index)
                    ? 'linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%)'
                    : 'transparent',
                  border: `2px solid ${tech.color}`,
                  borderRadius: '15px',
                  padding: '20px',
                  transform: visibleTechs.includes(index)
                    ? hoveredTech === index ? 'scale(1.05) translateY(-5px)' : 'scale(1) translateY(0)'
                    : 'scale(0.8) translateY(20px)',
                  opacity: visibleTechs.includes(index) ? 1 : 0,
                  transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
                  cursor: 'pointer',
                  position: 'relative',
                  overflow: 'hidden',
                  boxShadow: hoveredTech === index
                    ? `0 10px 30px ${tech.color}40`
                    : `0 5px 15px ${tech.color}20`
                }}
                onMouseEnter={() => setHoveredTech(index)}
                onMouseLeave={() => setHoveredTech(null)}
              >
                <div style={{
                  position: 'absolute',
                  top: '-50%',
                  right: '-50%',
                  width: '100%',
                  height: '100%',
                  background: `radial-gradient(circle, ${tech.color}15 0%, transparent 70%)`,
                  transform: hoveredTech === index ? 'scale(1)' : 'scale(0)',
                  transition: 'transform 0.4s ease'
                }}></div>

                <div style={{
                  fontSize: '40px',
                  marginBottom: '10px',
                  position: 'relative',
                  zIndex: 1,
                  transform: hoveredTech === index ? 'rotate(360deg)' : 'rotate(0deg)',
                  transition: 'transform 0.6s ease'
                }}>
                  {tech.icon}
                </div>

                <h3 style={{
                  color: tech.color,
                  margin: '0 0 10px 0',
                  position: 'relative',
                  zIndex: 1,
                  fontSize: '20px',
                  fontWeight: 'bold'
                }}>
                  {tech.name}
                </h3>

                <p style={{
                  color: '#666',
                  margin: '0 0 15px 0',
                  position: 'relative',
                  zIndex: 1,
                  fontSize: '14px',
                  lineHeight: '1.5'
                }}>
                  {tech.description}
                </p>

                <div style={{
                  width: '100%',
                  height: '8px',
                  background: '#e0e0e0',
                  borderRadius: '4px',
                  overflow: 'hidden',
                  position: 'relative',
                  zIndex: 1
                }}>
                  <div style={{
                    width: `${tech.level}%`,
                    height: '100%',
                    background: `linear-gradient(90deg, ${tech.color}, ${tech.color}dd)`,
                    borderRadius: '4px',
                    transition: 'width 1s ease-in-out',
                    position: 'relative'
                  }}>
                    <div style={{
                      position: 'absolute',
                      top: 0,
                      left: 0,
                      right: 0,
                      bottom: 0,
                      background: 'linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent)',
                      animation: hoveredTech === index ? 'shimmer 1.5s infinite' : 'none'
                    }}></div>
                  </div>
                </div>

                <div style={{
                  textAlign: 'right',
                  marginTop: '5px',
                  fontSize: '12px',
                  color: tech.color,
                  fontWeight: 'bold',
                  position: 'relative',
                  zIndex: 1
                }}>
                  {tech.level}% освоено
                </div>
              </div>
            ))}
          </div>

          <div style={{
            background: '#1e1e1e',
            borderRadius: '10px',
            padding: '20px',
            margin: '30px 0',
            fontFamily: 'Monaco, Consolas, monospace',
            fontSize: '14px',
            color: '#00ff00',
            position: 'relative',
            overflow: 'hidden'
          }}>
            <div style={{
              position: 'absolute',
              top: '10px',
              right: '15px',
              display: 'flex',
              gap: '8px'
            }}>
              <div style={{ width: '12px', height: '12px', borderRadius: '50%', background: '#ff5f56' }}></div>
              <div style={{ width: '12px', height: '12px', borderRadius: '50%', background: '#ffbd2e' }}></div>
              <div style={{ width: '12px', height: '12px', borderRadius: '50%', background: '#27ca3f' }}></div>
            </div>

            <div style={{
              color: '#666',
              marginBottom: '10px',
              fontSize: '12px'
            }}>
              📁 models.py
            </div>

            <pre style={{
              margin: 0,
              whiteSpace: 'pre-wrap',
              minHeight: '120px'
            }}>
              {codeAnimation}
              <span style={{
                opacity: codeAnimation ? 1 : 0,
                animation: 'blink 1s infinite'
              }}>_</span>
            </pre>
          </div>
        </div>
      </div>

    </Container>

    <style jsx>{`
      @keyframes bounce {
        0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
        40% { transform: translateY(-10px); }
        60% { transform: translateY(-5px); }
      }

      @keyframes shimmer {
        0% { transform: translateX(-100%); }
        100% { transform: translateX(100%); }
      }

      @keyframes blink {
        0%, 50% { opacity: 1; }
        51%, 100% { opacity: 0; }
      }
    `}</style>
  </Main>
}

export default Technologies
