'use client'

import { motion } from 'framer-motion'
import { useChat } from 'ai/react';
import ChatComponent from '@/components/ChatComponent';
import { Send, Brain, LineChart, Workflow } from 'lucide-react';
import Link from 'next/link';

export default function Home() {
  const fadeInUp = {
    initial: { opacity: 0, y: 20 },
    animate: { opacity: 1, y: 0 },
    transition: { duration: 0.5 }
  }

  const staggerContainer = {
    animate: {
      transition: {
        staggerChildren: 0.1
      }
    }
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-[#0A0A1F] via-[#1A1A3F] to-[#0A0A1F] overflow-hidden">
      {/* Efeitos de Background */}
      <div className="fixed inset-0 z-0">
        <div className="absolute inset-0 bg-[url('/grid.svg')] opacity-10" />
        <motion.div 
          className="absolute top-0 -left-40 w-[500px] h-[500px] bg-purple-500/10 rounded-full blur-[120px]"
          animate={{
            opacity: [0.5, 0.8, 0.5],
            scale: [1, 1.2, 1]
          }}
          transition={{
            duration: 8,
            repeat: Infinity,
            ease: "easeInOut"
          }}
        />
        <motion.div 
          className="absolute bottom-0 -right-40 w-[500px] h-[500px] bg-blue-500/10 rounded-full blur-[120px]"
          animate={{
            opacity: [0.5, 0.8, 0.5],
            scale: [1, 1.2, 1]
          }}
          transition={{
            duration: 8,
            repeat: Infinity,
            ease: "easeInOut",
            delay: 4
          }}
        />
      </div>

      {/* Header */}
      <motion.nav 
        initial={{ y: -20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.5 }}
        className="fixed top-0 left-0 right-0 z-50 bg-black/5 backdrop-blur-xl border-b border-white/5"
      >
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <Link href="#" className="text-2xl font-bold">
              <span className="gradient-text">All</span>
              <span className="text-white">Devs</span>
            </Link>
            <div className="hidden md:flex items-center gap-8">
              <Link href="#solucoes" className="nav-link">Soluções</Link>
              <Link href="#tecnologias" className="nav-link">Tecnologias</Link>
              <Link href="#projetos" className="nav-link">Projetos</Link>
              <Link href="#equipe" className="nav-link">Equipe</Link>
              <Link href="#contato" className="nav-link">Contato</Link>
            </div>
            <div className="flex items-center gap-4">
              <Link href="/budget" className="glass-button">
                Orçamento
              </Link>
              <Link href="#contato" className="glass-button-primary">
                Iniciar Projeto
              </Link>
            </div>
          </div>
        </div>
      </motion.nav>

      {/* Hero Section */}
      <section className="relative pt-32 pb-20 md:pt-48 md:pb-32">
        <div className="container mx-auto px-6">
          <div className="max-w-4xl mx-auto text-center">
            <motion.h1 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.7 }}
              className="text-4xl md:text-7xl font-bold mb-8"
            >
              <span className="gradient-text">Transformando Ideias</span>
              <br />
              <span className="text-white">com Tecnologia e IA</span>
            </motion.h1>
            <motion.p 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.7, delay: 0.2 }}
              className="text-lg md:text-xl text-white/70 mb-12"
            >
              Desenvolvemos soluções inovadoras combinando expertise técnica com 
              Inteligência Artificial para criar o futuro digital.
            </motion.p>
            <motion.div 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.7, delay: 0.4 }}
              className="flex flex-col md:flex-row gap-4 justify-center"
            >
              <Link href="#projetos" className="glass-button-primary">
                Ver Projetos
              </Link>
              <Link href="#contato" className="glass-button">
                Fale Conosco
              </Link>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Tecnologias Section */}
      <section id="tecnologias" className="py-20 relative">
        <div className="container mx-auto px-6">
          <motion.h2 
            variants={fadeInUp}
            initial="initial"
            whileInView="animate"
            viewport={{ once: true }}
            className="section-title"
          >
            Nossa Stack
          </motion.h2>
          <motion.div 
            variants={staggerContainer}
            initial="initial"
            whileInView="animate"
            viewport={{ once: true }}
            className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-6 mt-16"
          >
            {[
              { name: "Python", icon: "/tech/Python.svg", category: "Backend & IA" },
              { name: "TypeScript", icon: "/tech/TypeScript.svg", category: "Frontend & Backend" },
              { name: "React", icon: "/tech/React.svg", category: "Frontend" },
              { name: "React Native", icon: "/tech/React.svg", category: "Mobile" },
              { name: "Next.js", icon: "/tech/Next.js.svg", category: "Frontend" },
              { name: "PHP", icon: "/tech/PHP.svg", category: "Backend" },
              { name: "Rust", icon: "/tech/Rust.svg", category: "Performance" },
              { name: "Node.js", icon: "/tech/Node.js.svg", category: "Backend" },
              { name: "TensorFlow", icon: "/tech/TensorFlow.svg", category: "Machine Learning" },
              { name: "PostgreSQL", icon: "/tech/PostgresSQL.svg", category: "Database" },
              { name: "MongoDB", icon: "/tech/MongoDB.svg", category: "Database" },
              { name: "Firebase", icon: "/tech/Firebase.svg", category: "Database" },
              { name: "Docker", icon: "/tech/Docker.svg", category: "DevOps" },
              { name: "AWS", icon: "/tech/AWS.svg", category: "Cloud" },
              { name: "Tailwind CSS", icon: "/tech/Tailwind CSS.svg", category: "Styling" }
            ].map((tech, index) => (
              <motion.div
                key={index}
                variants={fadeInUp}
                className="tech-card group"
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                <motion.div 
                  className="relative h-16 w-16 mx-auto mb-4"
                  whileHover={{ scale: 1.1 }}
                  transition={{ type: "spring", stiffness: 300 }}
                >
                  <img
                    src={tech.icon}
                    alt={tech.name}
                    className="w-full h-full object-contain"
                  />
                </motion.div>
                <h3 className="text-white font-medium text-lg mb-1">{tech.name}</h3>
                <p className="text-white/50 text-sm">{tech.category}</p>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* Soluções com IA */}
      <section id="solucoes" className="py-20 bg-black/20">
        <div className="container mx-auto px-6">
          <motion.h2 
            variants={fadeInUp}
            initial="initial"
            whileInView="animate"
            viewport={{ once: true }}
            className="section-title"
          >
            Soluções Inteligentes
          </motion.h2>
          <motion.div 
            variants={staggerContainer}
            initial="initial"
            whileInView="animate"
            viewport={{ once: true }}
            className="grid md:grid-cols-2 lg:grid-cols-3 gap-8 mt-16"
          >
            {[
              {
                title: "IA Generativa",
                description: "Criação de conteúdo e automação inteligente com modelos de linguagem avançados",
                icon: <Brain className="w-12 h-12 text-purple-400" />
              },
              {
                title: "Análise Preditiva",
                description: "Tomada de decisão baseada em dados com algoritmos de Machine Learning",
                icon: <LineChart className="w-12 h-12 text-blue-400" />
              },
              {
                title: "Automação de Processos",
                description: "Otimização de fluxos de trabalho com RPA e IA",
                icon: <Workflow className="w-12 h-12 text-pink-400" />
              }
            ].map((solution, index) => (
              <motion.div
                key={index}
                variants={fadeInUp}
                className="solution-card"
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                <motion.div 
                  className="mb-6"
                  whileHover={{ scale: 1.1, y: -2 }}
                  transition={{ type: "spring", stiffness: 300 }}
                >
                  {solution.icon}
                </motion.div>
                <h3 className="text-xl font-semibold text-white mb-4">{solution.title}</h3>
                <p className="text-white/60">{solution.description}</p>
              </motion.div>
            ))}
          </motion.div>
      </div>
      </section>

      {/* Projetos */}
      <section id="projetos" className="py-20">
        <div className="container mx-auto px-4 sm:px-6">
          <motion.h2 
            variants={fadeInUp}
            initial="initial"
            whileInView="animate"
            viewport={{ once: true }}
            className="section-title"
          >
            Projetos em Destaque
          </motion.h2>
          <motion.div 
            variants={staggerContainer}
            initial="initial"
            whileInView="animate"
            viewport={{ once: true }}
            className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-16"
          >
            {[
              {
                title: "SendAny",
                description: "Plataforma que une Gist, Pastebin e Drive em uma única interface",
                tech: ["Next.js", "Serverless", "React", "PostgreSQL"],
                image: "/images/sendany.png"
              },
              {
                title: "pair.codes",
                description: "IDE + Terminal + IA: A revolução no desenvolvimento de software",
                tech: ["TypeScript", "TensorFlow", "PostgreSQL", "Electron", "Rust"],
                image: "/images/pair-codes.png"
              }
            ].map((project, index) => (
              <motion.div
                key={index}
                variants={fadeInUp}
                className="project-card group"
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                <div className="relative h-48 sm:h-64 mb-6 overflow-hidden rounded-xl">
                  <motion.img
                    src={project.image}
                    alt={project.title}
                    className="absolute inset-0 w-full h-full object-cover object-center transition-transform duration-500"
                    whileHover={{ scale: 1.1 }}
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/40 to-transparent" />
                </div>
                <h3 className="text-xl sm:text-2xl font-semibold text-white mb-3">{project.title}</h3>
                <p className="text-white/60 mb-4 text-sm sm:text-base">{project.description}</p>
                <div className="flex flex-wrap gap-2">
                  {project.tech.map((t, i) => (
                    <span key={i} className="tech-tag">{t}</span>
                  ))}
                </div>
              </motion.div>
            ))}
          </motion.div>
      </div>
      </section>

      {/* Seção de Equipe */}
      <section id="equipe" className="py-20">
        <div className="container mx-auto px-4 sm:px-6">
          <motion.h2 
            variants={fadeInUp}
            initial="initial"
            whileInView="animate"
            viewport={{ once: true }}
            className="section-title mb-4"
          >
            A Dupla Dinâmica
          </motion.h2>
          <motion.p
            variants={fadeInUp}
            initial="initial"
            whileInView="animate"
            viewport={{ once: true }}
            className="text-center text-white/70 mb-16 max-w-2xl mx-auto"
          >
            Somos uma dupla não convencional unida pela paixão por código e pela vontade 
            de fazer diferente. Com um sorriso no rosto e determinação no coração, 
            transformamos desafios em oportunidades.
          </motion.p>
          <motion.div 
            variants={staggerContainer}
            initial="initial"
            whileInView="animate"
            viewport={{ once: true }}
            className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-4xl mx-auto"
          >
            {[
              {
                name: "Caio Guerras",
                role: "Fundador & Visionário",
                image: "/images/caio.jpeg",
                description: "O idealizador do AllDevs que acredita que todo problema tem solução - e se não tem, a gente cria uma! Apaixonado por tecnologia e inovação, sempre com uma ideia nova na manga.",
                social: {
                  instagram: "https://instagram.com/ocaioguerras",
                  telegram: "https://t.me/ocaioguerras",
                  linkedin: "https://linkedin.com/in/ocaioguerras"
                }
              },
              {
                name: "Rosiel Victor",
                role: "Desenvolvedor Full Stack",
                image: "/images/rosiel.jpg",
                description: "O mago do código que transforma café em software. Com um olhar técnico afiado e criatividade sem limites, faz acontecer o que parecia impossível.",
                social: {
                  github: "https://github.com/misterioso013",
                  twitter: "https://twitter.com/RVictor013",
                  linkedin: "https://linkedin.com/in/rosielvictor"
                }
              }
            ].map((member, index) => (
              <motion.div
                key={index}
                variants={fadeInUp}
                className="glass-effect rounded-xl overflow-hidden group"
                whileHover={{ scale: 1.02 }}
              >
                <div className="aspect-[4/3] relative overflow-hidden">
                  <motion.img
                    src={member.image}
                    alt={member.name}
                    className="absolute inset-0 w-full h-full object-cover object-center transition-transform duration-500"
                    whileHover={{ scale: 1.1 }}
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/40 to-transparent" />
                  <motion.div 
                    initial={{ opacity: 0 }}
                    whileInView={{ opacity: 1 }}
                    className="absolute bottom-0 left-0 right-0 p-6 transform translate-y-6 group-hover:translate-y-0 transition-transform duration-300"
                  >
                    <h3 className="text-2xl font-bold text-white mb-2">{member.name}</h3>
                    <p className="text-purple-300">{member.role}</p>
                  </motion.div>
                </div>
                <div className="p-6">
                  <p className="text-white/80 mb-6 leading-relaxed">{member.description}</p>
                  <div className="flex gap-4">
                    {member.name === "Caio Guerras" ? (
                      <>
                        <motion.a
                          whileHover={{ scale: 1.1, y: -2 }}
                          whileTap={{ scale: 0.95 }}
                          href={member.social.instagram}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="glass-effect p-2 rounded-full hover:bg-white/20 transition-colors"
                        >
                          <img src="/tech/instagram.svg" alt="Instagram" className="w-5 h-5" />
                        </motion.a>
                        <motion.a
                          whileHover={{ scale: 1.1, y: -2 }}
                          whileTap={{ scale: 0.95 }}
                          href={member.social.telegram}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="glass-effect p-2 rounded-full hover:bg-white/20 transition-colors"
                        >
                          <Send className="w-5 h-5" />
                        </motion.a>
                      </>
                    ) : (
                      <motion.a
                        whileHover={{ scale: 1.1, y: -2 }}
                        whileTap={{ scale: 0.95 }}
                        href={member.social.github}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="glass-effect p-2 rounded-full hover:bg-white/20 transition-colors"
                      >
                        <img src="/tech/GitHub.svg" alt="GitHub" className="w-5 h-5" />
                      </motion.a>
                    )}
                    <motion.a
                      whileHover={{ scale: 1.1, y: -2 }}
                      whileTap={{ scale: 0.95 }}
                      href={member.social.linkedin}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="glass-effect p-2 rounded-full hover:bg-white/20 transition-colors"
                    >
                      <img src="/tech/linkedin.svg" alt="LinkedIn" className="w-5 h-5" />
                    </motion.a>
                    {member.name === "Rosiel Victor" && (
                      <motion.a
                        whileHover={{ scale: 1.1, y: -2 }}
                        whileTap={{ scale: 0.95 }}
                        href={member.social.twitter}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="glass-effect p-2 rounded-full hover:bg-white/20 transition-colors"
                      >
                        <img src="/tech/twitter.svg" alt="Twitter" className="w-5 h-5" />
                      </motion.a>
                    )}
                  </div>
                </div>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* Contato com Chat */}
      <section id="contato" className="py-20 bg-black/20">
        <div className="container mx-auto px-4 sm:px-6">
          <div className="max-w-4xl mx-auto">
            <motion.h2 
              variants={fadeInUp}
              initial="initial"
              whileInView="animate"
              viewport={{ once: true }}
              className="section-title mb-12"
            >
              Fale com nosso Assistente
            </motion.h2>
            <ChatComponent />
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-8 border-t border-white/5">
        <div className="container mx-auto px-6">
          <div className="flex flex-col md:flex-row justify-between items-center gap-4">
            <p className="text-white/60">&copy; {new Date().getFullYear()} AllDevs. Todos os direitos reservados.</p>
            <div className="flex gap-6">
              <Link href="https://github.com/alldevs" 
                target="_blank"
                rel="noopener noreferrer"
                className="text-white/60 hover:text-white transition-colors"
              >
                GitHub
              </Link>
              <Link href="https://linkedin.com/company/alldevsbr"
                target="_blank"
                rel="noopener noreferrer" 
                className="text-white/60 hover:text-white transition-colors"
              >
                LinkedIn
              </Link>
            </div>
          </div>
        </div>
      </footer>
    </main>
  )
}
