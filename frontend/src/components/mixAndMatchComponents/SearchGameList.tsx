import React from "react";
import usePoketStore from "../../stores/poketStore";
import GameCard from "../commonUseComponents/GameCard";
import style from "./MixandMatch.module.css";
import useUserStore from "../../stores/userStore";
import useMixAndMatchStore from "../../stores/mixAndMatchStore";
import { useNavigate } from 'react-router-dom'; // useNavigate 훅 추가



const SearchGameList: React.FC = () => {
  const cartItems = usePoketStore((state) => state.cartItems);

  // axios 요청을 위한 requestData 생성
  const userId = useUserStore().user?.userId;

  const gameIdAndTagDtoList = [];
  for (const item of cartItems) {
    gameIdAndTagDtoList.push({
      gameId: item.gameId,
      tagList: item.tagsAll,
    });
  }

  const requestData = {
    userId,
    gameIdAndTagDtoList
  };

  const { fetchData } = useMixAndMatchStore();

  const HandleOnClick = () => {
    fetchData(requestData);
  };

  const navigate = useNavigate(); // useNavigate 인스턴스화

  const handleClickGame = (gameId: number) => {
    navigate(`/detail/${gameId}`)
  }

  const handleGoToMain = () => {
    navigate('/');
  }

  // cartItems가 비어있을 경우 메세지를 표시
  if (cartItems.length === 0) {
    return (
      <div className={style.box} style={{ height: '200px', display: 'flex', justifyContent: 'center', alignItems: 'center', flexDirection: 'column' }}>
        <p className="mt-[70px] mb-[30px]">게임을 담아주세요!</p>
        <button className={style.topicBtn} onClick={handleGoToMain}>담으러 가기</button>
      </div>
    );
  }

  return (
    <div className={style.box} style={{ height: '275px' }}>
      <div className={style.gameList}>
        {cartItems.map((item, index: number) => (
          <GameCard
            key={index}
            gameId={item.gameId}
            imageUrl={item.imageUrl}
            title={item.title}
            price={`₩ ${item.price}`}
            tags={item.tagsAll?.filter(tag => tag.codeId === "GEN").map(tag => tag.tagName) ?? []}
            tagsAll={item.tagsAll}
            likes={0} 
            onGameClick={handleClickGame}
            isPrefer={false} 
            developer={item.developer}
            beforPrice={`₩ ${item.price}`}
          />
        ))}
      </div>
      <button className={style.topicBtn} onClick={HandleOnClick}> Mix! </button>
    </div>
  );
};

export default SearchGameList;