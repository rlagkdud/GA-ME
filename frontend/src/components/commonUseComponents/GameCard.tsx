// 장현욱

import { motion } from 'framer-motion'
import { useState } from 'react';
import  usePoketStore  from './../../stores/poketStore';
import style from './GameCard.module.css'

interface TagDto {
  codeId:string
  tagId:number
  tagName:string
}

// 타입스크립트 타입 프롭받을 타입 정의
interface GameCardProps {
  gameId: number;
  imageUrl: string;
  title: string;
  price: string;
  tagsAll?: TagDto[] | null;
  tags: string[];
  likes: number;
  onGameClick: (gameId: number) => void;
}


// 타입스크립트식 선언
const GameCard: React.FC<GameCardProps> = ({ gameId, imageUrl, title, price, tagsAll, tags, likes, onGameClick }) => {

  const [isHovered, setIsHovered] = useState(false);
  const { addItem } = usePoketStore();

  const handleAddToCart = (event: React.MouseEvent<HTMLButtonElement>) => {
    event.stopPropagation(); // 이벤트 버블링 중지
    const itemToAdd = { gameId, imageUrl, title, price, tagsAll };
    addItem(itemToAdd);
  };
  
  const hoverEffects = {
    scale: [1, 1.1], // 호버시 크기 설정
    transition: { duration: 0.3 },
  };
  
  const overlayVariants = {
    hidden: { opacity: 0, backdropFilter: 'none' },
    visible: { opacity: 1, backdropFilter: 'blur(5px)' },
  };

  

  return (
    <motion.div
      className={`${style.card} w-48 m-2 rounded overflow-hidden text-white text-center relative cursor-pointer`}
      whileHover={hoverEffects}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      onClick={() => onGameClick(gameId)}
    >
      <div className={`${style.card} w-48 rounded overflow-hidden text-white text-center`}>
        <img src={imageUrl} alt={title} className="w-full" />
        <div className="p-2">
          <h3 className="text-base">{title}</h3>
          <p className="text-xs">{price}</p>
        </div>
      </div>      {isHovered && (
        <motion.div
          className="absolute inset-0 bg-black bg-opacity-50 flex flex-col justify-between p-2"
          variants={overlayVariants}
          initial="hidden"
          animate="visible"
          exit="hidden"
        >
          <div className="flex justify-center items-center space-x-2">
            {/* Icons */}
            <button className="rounded-full p-2">
              {/* Heart Icon */}
              <img src={'./Like.png'} alt={'Like'}></img>
            </button>
            <motion.button className="rounded-full p-2" onClick={(event) => handleAddToCart(event)}
            whileHover={{ scale: 1.2, rotate: 360 }}
            whileTap={{
              scale: 0.8,
              // rotate: -90,
              borderRadius: "100%"
            }} >
              {/* Save Icon */}
              <img src={'./Cart.png'} alt={'Cart'}></img>
            </motion.button>
            <button className="rounded-full p-2">
              {/* Remove Icon */}
              <img src={'./NotLike.png'} alt={'NotLike'}></img>
            </button>
          </div>
          <div className="flex justify-center items-center">
            {/* Tag container */}
            <div >
              {/* Tags */}
              {tags.map((tag: string, index: number) => (
                <span key={index} className="bg-black bg-opacity-50 rounded px-2 py-1 text-xs font-semibold mx-1 inline-block">{`#${tag}`}
                </span>))}
            </div>
          </div>
          <div className="flex justify-center items-center mb-2">
            {/* Likes */}
            <span>{`좋아요 ${likes}`}</span>
          </div>
        </motion.div>
      )}
    </motion.div>
  );
};

export default GameCard;