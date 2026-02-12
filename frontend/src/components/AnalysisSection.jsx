import React, { useState } from 'react';
import { Sparkles, Cpu, ChevronDown, ChevronUp } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const AnalysisSection = ({ onAnalyze, isAnalyzing, analysisText, lastUpdated }) => {
    const [expanded, setExpanded] = useState(false);

    // Auto-expand when results arrive
    React.useEffect(() => {
        if (analysisText && !isAnalyzing) {
            setExpanded(true);
        }
    }, [analysisText, isAnalyzing]);

    return (
        <div className="glass-card rounded-2xl p-6 border-t border-t-blue-500/30 relative overflow-hidden transition-all duration-500">

            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 relative z-10">

                {/* Title & Status */}
                <div>
                    <h2 className="text-xl font-bold text-slate-100 flex items-center gap-2">
                        <Sparkles className="text-blue-400" size={20} />
                        市場分析
                    </h2>
                    <p className="text-slate-400 text-sm mt-1">
                        {analysisText
                            ? `最新觀點: ${lastUpdated || '剛剛'}`
                            : "點擊「手動觸發分析」以獲取 AI 市場預測"}
                    </p>
                </div>

                {/* Actions */}
                <div className="flex items-center gap-3">
                    <button
                        onClick={onAnalyze}
                        disabled={isAnalyzing}
                        className={`
                            relative px-6 py-2.5 rounded-xl font-bold text-sm tracking-wide transition-all duration-300
                            ${isAnalyzing
                                ? 'bg-slate-800 text-slate-500 cursor-not-allowed'
                                : 'bg-blue-600 hover:bg-blue-500 text-white shadow-lg shadow-blue-500/25 active:scale-95'
                            }
                        `}
                    >
                        {isAnalyzing ? (
                            <span className="flex items-center gap-2">
                                <Cpu className="animate-spin" size={16} />
                                分析中...
                            </span>
                        ) : (
                            "手動觸發分析"
                        )}
                    </button>

                    {analysisText && (
                        <button
                            onClick={() => setExpanded(!expanded)}
                            className="p-2.5 rounded-xl bg-slate-800/50 hover:bg-slate-700 text-slate-400 hover:text-white transition-colors border border-slate-700"
                        >
                            {expanded ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
                        </button>
                    )}
                </div>
            </div>

            {/* Expandable Content Area */}
            <AnimatePresence>
                {expanded && analysisText && (
                    <motion.div
                        initial={{ height: 0, opacity: 0, marginTop: 0 }}
                        animate={{ height: "auto", opacity: 1, marginTop: 24 }}
                        exit={{ height: 0, opacity: 0, marginTop: 0 }}
                        className="overflow-hidden"
                    >
                        <div className="bg-slate-900/50 rounded-xl p-5 border border-slate-800/50">
                            <div className="flex items-center gap-2 mb-3 text-xs font-mono text-emerald-400 uppercase tracking-wider">
                                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
                                AI_INSIGHT_RECEIVED
                            </div>
                            <div className="text-slate-300 leading-relaxed whitespace-pre-wrap font-sans text-sm md:text-base">
                                {analysisText}
                            </div>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>

            {/* Background decoration matches Pencil design vibes */}
            <div className="absolute -right-20 -top-20 w-64 h-64 bg-blue-500/5 rounded-full blur-3xl pointer-events-none"></div>
        </div>
    );
};

export default AnalysisSection;
